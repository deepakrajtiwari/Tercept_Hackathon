import openai
import base64

# Set your OpenAI API key
openai.api_key = "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"

# Convert image to base64
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Send image to GPT-4 Vision model
def get_caption_and_hashtags(image_path):
    base64_image = encode_image(image_path)
    
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Generate a witty caption and relevant hashtags for this image."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )

    return response.choices[0].message.content.strip()

# Prompt user for image path
if __name__ == "__main__":
    image_path = input("Enter the path to your image: ")
    result = get_caption_and_hashtags(image_path)
    print("\n📝 GPT-4 Output:\n")
    print(result)
