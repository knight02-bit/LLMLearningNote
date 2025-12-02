"""
使用方法
python check_versions.py
或者指定路径
python check_versions.py /path/to/your/project
"""


import os
import sys
import ast
import importlib.metadata
import argparse
from stdlib_list import stdlib_list  # 建议安装 stdlib-list 库，如果没有安装，脚本会回退到简单过滤

# 常用库的 import 名称到 pip 包名的映射
# 这个列表可以持续补充
IMPORT_MAPPING = {
    'PIL': 'Pillow',
    'dotenv': 'python-dotenv',
    'rest_framework': 'djangorestframework',
    'corsheaders': 'django-cors-headers',
    'cv2': 'opencv-python',
    'skimage': 'scikit-image',
    'sklearn': 'scikit-learn',
    'yaml': 'PyYAML',
    'bs4': 'beautifulsoup4',
    'google.protobuf': 'protobuf',
    'telegram': 'python-telegram-bot',
    'dateutil': 'python-dateutil',
    'dj_database_url': 'dj-database-url',
    'mysqldb': 'mysqlclient',
    'psycopg2': 'psycopg2-binary',
    # LlamaIndex 相关
    'llama_index': 'llama-index',
}

def get_stdlib_modules():
    """获取当前 Python 版本的标准库列表"""
    try:
        # 尝试获取准确的标准库列表
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        return set(stdlib_list(version))
    except ImportError:
        # 如果没有安装 stdlib-list，使用 sys.builtin_module_names 和一些常见的
        # 这是一个兜底方案
        common_stdlib = {
            'os', 'sys', 're', 'json', 'time', 'math', 'datetime', 'typing', 'pathlib',
            'argparse', 'logging', 'subprocess', 'shutil', 'hashlib', 'random', 'uuid',
            'threading', 'multiprocessing', 'io', 'collections', 'functools', 'itertools',
            'copy', 'abc', 'enum', 'warnings', 'inspect', 'traceback', 'contextlib',
            'unittest', 'doctest', 'pdb', 'site', 'builtins', 'urllib', 'http', 'email',
            'xml', 'html', 'socket', 'ssl', 'sqlite3', 'csv', 'tarfile', 'zipfile', 'gzip'
        }
        return set(sys.builtin_module_names) | common_stdlib

def get_imports_from_file(file_path):
    """从 Python 文件中提取 import 语句"""
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # 处理 from . import x 或 from .. import y
                    if node.level > 0: 
                        continue
                    imports.add(node.module.split('.')[0])
    except SyntaxError:
        print(f"⚠️  语法错误，跳过文件: {file_path}")
    except Exception as e:
        # print(f"⚠️  解析错误 {file_path}: {e}")
        pass
    return imports

def scan_project_imports(root_dir, ignore_dirs=None):
    """扫描整个项目的 import"""
    if ignore_dirs is None:
        ignore_dirs = {'venv', '.venv', 'env', '.env', '.git', '__pycache__', 'node_modules', 'dist', 'build'}
        
    all_imports = set()
    
    print(f"🔍 开始扫描目录: {root_dir}")
    
    for root, dirs, files in os.walk(root_dir):
        # 修改 dirs 列表以原地过滤需要忽略的目录
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_imports = get_imports_from_file(file_path)
                all_imports.update(file_imports)
                
    return all_imports

def get_installed_version(package_name):
    """获取已安装包的版本"""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None

def main():
    parser = argparse.ArgumentParser(description='Python 项目依赖扫描工具')
    parser.add_argument('path', nargs='?', default='.', help='要扫描的项目根目录 (默认当前目录)')
    parser.add_argument('-o', '--output', default='requirements_freeze.txt', help='输出文件名')
    args = parser.parse_args()

    root_dir = os.path.abspath(args.path)
    
    if not os.path.exists(root_dir):
        print(f"❌ 错误: 目录不存在 {root_dir}")
        sys.exit(1)

    # 1. 扫描 Import
    imported_modules = scan_project_imports(root_dir)
    
    # 2. 获取标准库列表
    stdlib_modules = get_stdlib_modules()
    
    # 3. 过滤和版本检查
    requirements = []
    local_modules = set() # 记录可能是本地模块的名称
    
    # 先快速扫描一下根目录下的文件夹，判断哪些是本地模块
    for item in os.listdir(root_dir):
        if os.path.isdir(os.path.join(root_dir, item)) and os.path.exists(os.path.join(root_dir, item, '__init__.py')):
            local_modules.add(item)
        if item.endswith('.py'):
            local_modules.add(item[:-3])

    print(f"\n📦 正在检查包版本...")
    
    processed_packages = set()

    for module in sorted(imported_modules):
        # 过滤标准库
        if module in stdlib_modules:
            continue
            
        # 过滤本地模块
        if module in local_modules:
            continue
            
        # 获取映射后的包名
        package_name = IMPORT_MAPPING.get(module, module)
        
        # 避免重复处理
        if package_name in processed_packages:
            continue

        version = get_installed_version(package_name)
        
        if version:
            req_line = f"{package_name}=={version}"
            requirements.append(req_line)
            processed_packages.add(package_name)
            print(f"✅ {module:15} -> {package_name}=={version}")
        else:
            # 尝试全小写 (很多包名大小写不敏感)
            version_lower = get_installed_version(package_name.lower())
            if version_lower:
                req_line = f"{package_name.lower()}=={version_lower}"
                requirements.append(req_line)
                processed_packages.add(package_name.lower())
                print(f"✅ {module:15} -> {package_name.lower()}=={version_lower}")
            else:
                # 再次检查是否是本地子模块（有时 import x.y 这种形式）
                is_local = False
                for local in local_modules:
                    if module.startswith(local + '.'):
                        is_local = True
                        break
                
                if not is_local:
                    # 特殊处理：有些包就是无法直接通过 import name 找到 version
                    # 比如 llama_index 的一些插件，或者一些很怪的包
                    print(f"❓ 未找到版本: {module} (可能是未安装、本地模块或包名映射缺失)")

    # 4. 智能补充 (Heuristic)
    # 扫描当前环境中所有已安装的包，如果是特定前缀的（如 django-, flask-, llama-index-），自动添加
    # 这有助于捕获那些通过插件机制加载而没有直接 import 的包
    print("\n➕ 正在扫描关联插件包...")
    
    # 获取当前环境所有已安装的包
    try:
        installed_dists = list(importlib.metadata.distributions())
    except:
        installed_dists = []
        
    relevant_prefixes = ['django-', 'flask-', 'llama-index-', 'langchain-', 'starlette', 'uvicorn']
    
    for dist in installed_dists:
        name = dist.metadata['Name']
        if name in processed_packages:
            continue
            
        # 如果已识别的包中包含某个前缀（比如已识别了 django，那么把所有 django-xxx 都加进来）
        should_add = False
        for prefix in relevant_prefixes:
            if name.lower().startswith(prefix):
                should_add = True
                break
        
        # 或者，如果我们已经识别了某个主包（如 llama-index），那么把所有相关包都加进来
        if not should_add:
             for known_pkg in processed_packages:
                 if name.lower().startswith(known_pkg.lower() + '-'):
                     should_add = True
                     break

        if should_add:
            version = dist.version
            req_line = f"{name}=={version}"
            requirements.append(req_line)
            processed_packages.add(name)
            print(f"➕ 自动添加关联包: {name}=={version}")

    # 5. 写入文件
    output_path = os.path.join(root_dir, args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted(requirements)))
    
    print(f"\n📄 已生成依赖文件: {output_path}")

if __name__ == "__main__":
    main()