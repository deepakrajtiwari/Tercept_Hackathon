import openai
import base64
import random
import re

openai.api_key = ""

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def generate_response(image_path, company_name):
    base64_image = encode_image(image_path)
    messages = []

    score = random.randint(30, 100)

    caption_prompt = (
        f"Write a LinkedIn caption with 3 to 5 distinct sentences, based on the image and the company name: {company_name}. "
        f"Make it professional, witty, and reflective in tone. After the caption, add 3 to 5 relevant hashtags."
    )
    messages.append({"type": "text", "text": caption_prompt})

    if score < 50:
        analysis_prompt = (
            f"This LinkedIn post received a performance score of {score}/100 and did not perform well. "
            f"Suggest 2–3 brief reasons why it may have underperformed based on the image and the company context: \"{company_name}\"."
        )
    else:
        analysis_prompt = (
            f"This LinkedIn post received a performance score of {score}/100 and went viral. "
            f"Give 2–3 reasons why it likely performed well based on the image and the company context: \"{company_name}\"."
        )
    messages.append({"type": "text", "text": analysis_prompt})

    messages.append({
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
    })

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": messages}],
            max_tokens=600
        )

        output_text = response.choices[0].message.content.strip()

        if "I'm sorry" in output_text or "can't help" in output_text.lower():
            return {
                "score": score,
                "caption_and_hashtag": None,
                "virality": "⚠️ The AI could not generate a response. Try different image content or a clearer company name."
            }

        # Split the output roughly into two parts by detecting "Reasons" or similar keyword
        # You can adjust the regex or keywords if the model output format changes
        split_match = re.split(r'\n\*\*Reasons for.*?\*\*\n', output_text, maxsplit=1, flags=re.IGNORECASE)
        
        if len(split_match) == 2:
            caption_and_hashtag = split_match[0].strip()
            virality = "**Reasons for Performance:**\n" + split_match[1].strip()
        else:
            # fallback: just return whole output as caption_and_hashtag, no virality
            caption_and_hashtag = output_text
            virality = ""

    except Exception as e:
        return {
            "score": score,
            "caption_and_hashtag": None,
            "virality": f"❌ Error while generating response: {str(e)}"
        }

    return {
        "score": score,
        "caption_and_hashtag": caption_and_hashtag,
        "virality": virality
    }


if __name__ == "__main__":
    image_path = input("Enter the path to your LinkedIn post image: ").strip()
    company_name = input("Enter the company name: ").strip()

    result = generate_response(image_path, company_name)

    print(f"\n📊 Post Score: {result['score']}")
    print("\n📝 Caption and Hashtags:\n" + (result["caption_and_hashtag"] or "N/A"))
    print("\n📈 Virality Analysis:\n" + (result["virality"] or "N/A"))