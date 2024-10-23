from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import OpenAI
import time
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-proj-WvSahLslDzboC4B0voTNT3BlbkFJKMjungzLGxEDp42mXobo"))
thread = client.beta.threads.create()
MATH_ASSISTANT_ID = 'asst_bdUlFPzq2hcyaFPDuvsyBBkm'

url = 'https://rateiogarantido.com/wp-admin/post.php?post=707&action=edit'
email = 'rateiogarantido@gmail.com'
pwd = 'q,4>6xVbw&#:+Cy'

proxy = '45.127.248.127:5128'
options = webdriver.ChromeOptions()
options.add_argument(f'--proxy-server={proxy}')
driver = webdriver.Chrome(options=options)
driver.get(url)
while len(driver.find_elements(By.NAME, 'log')) <  1:
    time.sleep(1)
input_login = driver.find_element(By.NAME, 'log')
input_login.send_keys(email)
input_senha = driver.find_element(By.NAME, 'pwd')
input_senha.send_keys(pwd)
input_senha.send_keys(Keys.RETURN)
time.sleep(5)
progress_file = 'progress_2.txt'
credentials_file_2 = 'cursos_top.txt'

def edit(name_course, description_course):

    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'wpbody-content')))
    
    copy_product = driver.find_element(By.CSS_SELECTOR, '.submitduplicate')
    copy_product.click()
    time.sleep(1)
    print('certoooo')

    title = driver.find_element(By.NAME, 'post_title')
    title.clear()
    title.send_keys(name_course)


    title_yoast = driver.find_element(By.XPATH, "//*[@id='focus-keyword-input-metabox']")
    title_yoast.send_keys(Keys.CONTROL + 'a')
    title_yoast.send_keys(Keys.DELETE)
    text_title = str(name_course).split('–')
    title_yoast.send_keys(text_title[0])

    metadescription = driver.find_element(By.CSS_SELECTOR, "#yoast-google-preview-description-metabox > div > div > div > span")
    metadescription.send_keys(Keys.CONTROL + 'a')
    metadescription.send_keys(Keys.DELETE)
    metadescription.send_keys(description_course)

    save_button = driver.find_element(By.ID, 'publish')
    driver.execute_script("arguments[0].click();", save_button)


    frame = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'content_ifr')))
    driver.switch_to.frame(frame)
    description_field = driver.find_element(By.ID, 'tinymce')
    description_field.send_keys(Keys.CONTROL + 'a')
    description_field.send_keys(Keys.DELETE)
    description_field.send_keys(description_course)
    driver.switch_to.default_content()

    save_button = driver.find_element(By.ID, 'publish')
    driver.execute_script("arguments[0].click();", save_button)
    time.sleep(1)

###chat gpt ##

def submit_message(assistant_id, thread_1, user_message):
    client.beta.threads.messages.create(
        thread_id=thread_1.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )


def get_response(thread_2):
    return client.beta.threads.messages.list(thread_id=thread_2.id, order="asc")


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def pretty_print(messages):
    for m in messages:
        description = m.content[0].text.value
    return description
    
def chatgpt(course):
    run = submit_message(MATH_ASSISTANT_ID, thread, course)
    run = wait_on_run(run, thread)
    text = get_response(thread)
    response = pretty_print(text)
    return response

##save progress##        
def save_progress_2(line_number: int, progress_file: str):
    with open(progress_file, "w") as file:
        file.write(str(line_number))

def read_progress(progress_file: str) -> int:
    if os.path.exists(progress_file):
        with open(progress_file, "r") as file:
            return int(file.read().strip())
    return 0

try:
      start_line = read_progress(progress_file)
      with open(credentials_file_2, "r") as cred_file:

          for current_line, name_course in enumerate(cred_file):
              if current_line < start_line:
                  continue  # Pula as linhas já processadas
              
              description_chatgpt = chatgpt(name_course)
              description_course = str(description_chatgpt).strip()
              edit(name_course, description_course)   
              
              # Salva o progresso após processar cada linha
              save_progress_2(current_line + 1, progress_file)

except FileNotFoundError:
      print("Arquivo 'credentials.txt' não encontrado.")
except ValueError:
      print("Formato de credenciais inválido no arquivo 'credentials.txt'.")

# with open('name_courses.txt', 'r') as file:
#    for name_course in file:
#      description_chatgpt = chatgpt(name_course)
#      description_course = description_chatgpt.lstrip() 
#      edit(name_course, description_course)   
