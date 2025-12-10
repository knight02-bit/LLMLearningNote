## Create a Chroma service 创建 Chroma 服务

Create chroma_project/documents/chroma_service.py
创建 chroma_project/documents/chroma_service.py



```python
import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

class ChromaService:
    _client = None
    _collection = None
    
    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = chromadb.CloudClient(
                api_key=os.getenv("CHROMA_API_KEY"),
                tenant=os.getenv("CHROMA_TENANT"),
                database=os.getenv("CHROMA_DATABASE")
            )
        return cls._client
    
    @classmethod
    def get_collection(cls):
        if cls._collection is None:
            client = cls.get_client()
            cls._collection = client.get_or_create_collection(name="documents")
        return cls._collection
```

## Example: batch upload documents 示例：批量上传文档

In order to test the connection to Chroma, here is an example where we create an API endpoint /api/documents for uploading documents in batches. Now that the service is set up, you can create more functions that use Chroma. For example, you can add the following function to ChromaService:
为了测试与 Chroma 的连接，这里我们创建一个 API 端点 /api/documents ，用于批量上传文档。服务设置完成后，您可以创建更多使用 Chroma 的函数。例如，您可以将以下函数添加到 ChromaService 中：



```python
    ...
    @classmethod
    def add_documents(cls, ids, documents, metadatas):
        collection = cls.get_collection()
        collection.add(documents=documents, ids=ids, metadatas=metadatas) 
    ...
```

Now that the service is set up, you can create more functions that use Chroma. For this example, we will be creating a new Django app documents using the following command:
现在服务已经设置完毕，您可以创建更多使用 Chroma 的函数。在本例中，我们将使用以下命令创建一个新的 Django 应用文档 ：



```bash
python manage.py startapp documents
```

In chroma_project/documents/views.py, create a new view to handle POST requests:
在 chroma_project/documents/views.py 中，创建一个新视图来处理 POST 请求：



```python
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .chroma_service import ChromaService

@csrf_exempt
@require_http_methods(["POST"])
def add_documents(request):
    try:
        data = json.loads(request.body)
        
        ids = data['ids']
        documents = data['documents']
        metadatas = data['metadatas']
        ChromaService.add_documents(ids, documents, metadatas)
        
        return JsonResponse({
            'message': 'Documents added successfully',
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

## Configure URLs 配置 URL

Create chroma_project/documents/urls.py
创建 chroma_project/documents/urls.py



```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.add_documents, name='add_documents'),
]
```

In chroma_project/chroma_project/urls.py:
在 chroma_project/chroma_project/urls.py 中：



```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/documents/', include('documents.urls')),
]
```

## Test your API 测试您的 API

Run your app. 运行你的应用。



```bash
python manage.py runserver
```

You can now add documents to your Chroma collection using your new endpoint! You may need to modify this command if your app is running on a different port.
现在您可以使用新的端点向 Chroma 集合添加文档了！如果您的应用运行在不同的端口上，您可能需要修改此命令。



```bash
curl -X POST "http://localhost:8000/api/documents/" \
     -H "Content-Type: application/json" \
     -d '{
       "ids": ["1", "2"],
       "documents": ["Hello Chroma from Express.js!", "Second doc with different metadata"],
       "metadatas": [{ "category": "technology" }, { "category": "example" }]
     }'
```