# 常规转化文档:https://docling.com.cn/docling/examples/custom_convert/

import logging
import sys
import time
from pathlib import Path

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode

_log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("❌ 使用方法: 程序名 文件名.pdf")
        print("使用方法: geoCut.exe 文件名.pdf")
        sys.exit(1)

    pdf_filename = sys.argv[1]

    # 目标 PDF（文件名中间有空格）
    # input_doc_path = Path(r"d:\project\geoCut\Extract[16-21]金川集团二矿区1000m中段水平矿柱回采智能监测及对策研究结题报告(打印版) .pdf")
    # input_doc_path = Path(__file__).parent / "金川集团二矿区1000m中段水平矿柱回采智能监测及对策研究结题报告(打印版).pdf"

    base_dir = Path(__file__).parent
    input_doc_path = base_dir / "doc" / pdf_filename

    if not input_doc_path.exists():
        raise FileNotFoundError(f"未找到文件: {input_doc_path}")

    # 配置 PDF 解析管线：启用 OCR（中文）、表格结构识别、CPU 运行
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    try:
        pipeline_options.ocr_options.lang = ["ch_sim"]  # EasyOCR 中文（简体）
        pipeline_options.ocr_options.use_gpu = False     # 在多数 Windows 环境下使用 CPU 更稳妥
    except Exception:
        # 某些版本选项结构不同；若设置失败则保持默认 OCR
        pass

    pipeline_options.images_scale = 2.0
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=4,
        device=AcceleratorDevice.AUTO,
    )

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()
    conv_result = doc_converter.convert(input_doc_path)
    _log.info(f"Document converted in {time.time() - start_time:.2f} seconds.")

    # 导出到 scratch 目录
    output_dir = base_dir / "scratch"
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_result.input.file.stem

    # # 导出纯文本
    # txt_path = output_dir / f"{doc_filename}.txt"
    # txt_path.write_text(conv_result.document.export_to_text(), encoding="utf-8")
    # print(f"- {txt_path}")

    # 导出 Markdown
    md_refs_path = output_dir / f"{doc_filename}-with-image-refs.md"
    conv_result.document.save_as_markdown(md_refs_path, image_mode=ImageRefMode.REFERENCED)
    print("已导出 Markdown 文件:")
    print(f"- {md_refs_path}")
    

if __name__ == "__main__":
    main()