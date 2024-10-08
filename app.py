from flask import Flask, jsonify, request
from flask_cors import CORS
import openai
import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
# 使用 CORS 來允許所有來源
CORS(app)

# 定义 OpenAI 客户端
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 定义 download_count.json 文件的路径
file_path = os.path.join(os.path.dirname(__file__), 'download_count.json')

# 如果 download_count.json 不存在，创建并初始化 downloadNumber 为 0
def initialize_download_count():
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            json.dump({"downloadNumber": 0}, file)

# 读取 JSON 文件中的 downloadNumber
def read_download_number():
    with open(file_path, "r") as file:
        data = json.load(file)
        return data["downloadNumber"]

# 更新 JSON 文件中的 downloadNumber
def update_download_number(new_number):
    with open(file_path, "w") as file:
        json.dump({"downloadNumber": new_number}, file)

# 定义生成图像的路由
@app.route("/generate-image", methods=["POST"])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")

        # 初始化 download_count 文件
        initialize_download_count()

        # 读取当前的 downloadNumber
        downloadNumber = read_download_number()
        
        # 调用 OpenAI API 生成图像
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        
        # 发送 HTTP 请求下载图像
        image_response = requests.get(image_url)
        
        # 保存图像到本地
        image_filename = os.path.join(os.path.dirname(__file__), f"ai_img{downloadNumber}.png")
        with open(image_filename, "wb") as f:
            f.write(image_response.content)
        
        # 保存 prompt 到本地 JSON 文件
        prompt_filename = os.path.join(os.path.dirname(__file__), f"ai_img{downloadNumber}.json")
        with open(prompt_filename, "w") as f:
            json.dump({"prompt": prompt}, f)

        # 更新下载计数
        downloadNumber += 1
        update_download_number(downloadNumber)

        # 返回图像信息到前端
        return jsonify({
            "image_url": image_url,
            "image_local": image_filename,
            "prompt": prompt
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)