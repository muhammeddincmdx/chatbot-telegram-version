from llama_index import SimpleDirectoryReader, GPTVectorStoreIndex, LLMPredictor, PromptHelper
from llama_index import ServiceContext, StorageContext, load_index_from_storage
import os
import json
from langchain import OpenAI
os.environ["OPENAI_API_KEY"] = ""
import aiogram

bot_token = ""
bot = aiogram.Bot(token=bot_token)
dp = aiogram.Dispatcher(bot)

def create_index(path):
    max_input = 4096
    tokens = 1000
    chunk_size = 600
    max_chunk_overlap = 20

    prompt_helper = PromptHelper(max_input, tokens, tokens, max_chunk_overlap, chunk_size_limit=chunk_size)

    # Define LLM
    llmPredictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-ada-001", max_tokens=tokens))

    # Load data
    docs = SimpleDirectoryReader(path).load_data()

    service_context = ServiceContext.from_defaults(llm_predictor=llmPredictor, prompt_helper=prompt_helper)

    vectorIndex = GPTVectorStoreIndex.from_documents(documents=docs, service_context=service_context)
    vectorIndex.storage_context.persist(persist_dir="Store")
    return vectorIndex

create_index = create_index("Info")

def answerMe(question):
    storage_context = StorageContext.from_defaults(persist_dir="Store")
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
    response = query_engine.query(question)
    return response

@dp.message_handler(commands=["start"])
async def handle_start(message: aiogram.types.Message):
    await message.reply("Merhaba, ben Mekatronik Mühendisliği 1. sınıf öğrencileri için oluşturulmuş bir chatbotum. Sizlere derslerle ilgili bilgi sunabilirim.")

@dp.message_handler(commands=["quit"])
async def handle_quit(message: aiogram.types.Message):
    await message.reply("Görüşmek üzere!")

@dp.message_handler()
async def handle_message(message: aiogram.types.Message):
    question = message.text.lower()
    knowledge_dir = "Info/"
    files = os.listdir(knowledge_dir)
    found = False
    file_name = ""

    for file in files:
        if file.endswith(".txt"):
            with open(os.path.join(knowledge_dir, file), "r", encoding="utf-8") as f:
                content = f.read().lower()
                if any(word in content for word in question.split()):
                    found = True
                    file_name = file
                    break

    if found:
        response = answerMe(question)
        await message.reply(response)
    else:
        await message.reply("Bu konuda bilgim yok. Başka bir soru sormak ister misiniz?")

aiogram.executor.start_polling(dp)
