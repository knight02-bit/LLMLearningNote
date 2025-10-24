import torch
from transformers import Qwen3VLForConditionalGeneration, AutoProcessor

# 1. 加载模型
# model = Qwen3VLForConditionalGeneration.from_pretrained(
#     "Qwen/Qwen3-VL-2B-Thinking", dtype="auto", device_map="auto"
# )
# 官方推荐使用 flash_attention_2 来获得更好的加速和内存节省，尤其是在处理多图像和视频时
# Flash Attention 是一种更高效的注意力机制实现，能显著降低计算和显存开销
# 使用前需要安装: pip install flash-attn --no-build-isolation
model = Qwen3VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen3-VL-2B-Thinking",        # 模型路径
    dtype=torch.bfloat16,               # 明确指定使用 bfloat16 数据类型。这是一种16位浮点数，在训练和推理中能提供良好的数值稳定性和性能，现代大模型常用的选择
    attn_implementation="flash_attention_2", # 指定使用 Flash Attention 2 实现注意力机制
    device_map="auto",                  # 自动分配模型到设备（如GPU）
)

# 2. 加载处理器
# AutoProcessor: 一个自动处理器，它能根据模型名称自动加载正确的处理器。
# 处理器通常包含两个部分：
#   - Tokenizer: 将文本转换为模型能理解的数字 ID。
#   - Image Processor: 将图像转换为模型能理解的张量格式。
processor = AutoProcessor.from_pretrained("Qwen/Qwen3-VL-2B-Thinking")

# 3. 定义一个对话列表
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": "https://cdn.beekka.com/blogimg/asset/202509/bg2025092006.webp",
            },
            {"type": "text", "text": "描述这张图片"},
        ],
    }
]

# 4. 使用处理器将准备好的消息转换为模型输入的张量格式
inputs = processor.apply_chat_template(
    messages,                # 传入对话消息
    tokenize=True,           # 对文本进行分词，转换为数字 ID
    add_generation_prompt=True, # 在对话末尾添加一个特殊的生成提示符，告诉模型开始生成回答
    return_dict=True,        # 返回一个字典格式的数据，方便后续访问
    return_tensors="pt"      # 返回 PyTorch 张量格式
)

# 5. 将处理后的输入张量移动到模型所在的设备上
# 这一步是必须的，因为模型和数据必须在同一个设备上才能进行计算
inputs = inputs.to(model.device)

# 6. 调用模型的 generate 方法进行文本生成
# **inputs: 使用解包操作符将字典中的所有参数（如 input_ids, attention_mask, pixel_values 等）传递给 generate 方法
# max_new_tokens=128: 限制模型最多生成 128 个新的 token，用于控制输出长度，防止模型无限生成
generated_ids = model.generate(**inputs, max_new_tokens=128)


# 7. 后处理输出
generated_ids_trimmed = [
    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]

# 使用处理器的解码器，将新生成的 token ID 序列转换回可读的文本字符串
output_text = processor.batch_decode(
    generated_ids_trimmed,        # 传入裁剪后的 token ID
    skip_special_tokens=True,     # 跳过特殊的 token（如 <s>, </s>, <pad>），使输出更干净
    clean_up_tokenization_spaces=False # 不清理分词产生的多余空格，保持原始格式
)
print(output_text)