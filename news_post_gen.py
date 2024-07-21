from openai import OpenAI
from config import Config
import requests

NEWSAPI_API_KEY = Config.NEWSAPI_API_KEY

def get_recent_news(topic):
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={NEWSAPI_API_KEY}"
    response = requests.get(url)
    articles = response.json()["articles"]
    titles = [article["title"] for article in articles[:3]]
    urls = [article["url"] for article in articles[:3]]
    descriptions = [article["description"] for article in articles[:3]]
    print(f"news found: {"\n".join(titles)}")
    return {"titles":"\n".join(titles),
            "links":"\n".join(urls),
            "descriptions":"####\n".join(descriptions)}

class NewsPostGenerator():
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        return

    def get_news_topic(self, questions):
        prompt = """You are a thoughtful and polite conversationalist.
Keep the chat conversation going based on the last few messages. 
Determine the topic based on the last few messages.
The topic will then be used to select news articles.
Your answer should not contain more than three words."""
        messages=[
            {"role": "system", "content": prompt},
        ]
        messages.extend(
			{"role": "user", "content": question} for question in questions
		)
        response = self.client.chat.completions.create(
		    model = "gpt-4o-mini",
		    messages=messages,
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.7)
        return response.choices[0].message.content 
    
    def generate_post(self, topic):
        recent_news = get_recent_news(topic)

        prompt_title = f"Come up with an eye-catching headline for a post on the topic: {topic}. Answer in Russian. Add formattings and emojies to make it attractive post title at Telegram."
        response_title = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_title}],
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.7,
        )
        title = response_title.choices[0].message.content.strip()
        #print(f"post title: {title}")

        prompt_meta = f"Write a brief but informative meta description for the post with the title: {title}. Do not include title in the meta description. Answer in Russian. Add formattings and emojies to make it attractive post description at Telegram. This should be displayed in the fine printю"
        response_meta = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_meta}],
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.7,
        )
        meta_description = response_meta.choices[0].message.content.strip()
        #print(f"post meta: {meta_description}")

        prompt_post = f"Write a detailed and engaging blog post on {topic}, keeping in mind the following recent news:\n{recent_news}\n\n\n\n Use short paragraphs, subheadings, examples and keywords for better comprehension and SEO optimization. Answer in Russian. Add formattings and emojies to make it attractive post at Telegram. Do not generate text longer than 512 charachters."
        response_post = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_post}],
            max_tokens=512,
            n=1,
            stop=None,
            temperature=0.7,
        )
        post_content = response_post.choices[0].message.content.strip() + "\n" + recent_news['links']
        #print(f"post: {post_content}")

        return {
            "title": title,
            "meta_description": meta_description,
            "post_content": post_content
        }


    def get_answer(self, questions):
        #print(f"conversation: {questions}")
        topic = self.get_news_topic(questions)
        #print(f"news topic: {topic}")
        post = self.generate_post(topic)
        
        return f"{post['title']}\n\n{post['meta_description']}\n\n{post['post_content']}"

if __name__ == "__main__":
    generator = NewsPostGenerator()
    answer = generator.get_answer(['Да, хуже только Трамп, наверно.', 'Надо войну заканчивать. Война-это плозо', 'А ты читал Зайончковского?'])
    #print(answer)