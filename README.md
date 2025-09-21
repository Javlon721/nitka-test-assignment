Hi! 
I appriciate a chance to be a part of Nitka development team!

I listed all instructions in **Makefile** and it linked to my MAC OS.
So if you on linux or windows, you should change some commands

## To run this project you need:

1. Specify **GEMINI_API_KEY** inside **.env** folder. You can also specify **GEMINI_MODEL**

    Make sure that your **GEMINI_API_KEY** can handle 100 pdf files. If not there is /count endpoint
    to check how many pdfs extracted by GOOGLE GEMINI (because i can only handle 15 at time)

2. run `` make build `` to install all dependencies

3. run `` make extract `` to download pdf-files and extract metadata from them using google gemini models.
  
  Notice that for deadline and for simplicity, i used **arxiv** module to find pdf-files.
  So in future, it can be managed to other resourses

4. run `` make run `` to launch FastAPI project

5. Last, to see results, run `` make html ``, and click to url that this command suggests.

  Mine is -> "Serving HTTP on :: port 8001 (http://[::]:8001/) ..."

And the end, i want to say that if you will change API ports keep in mind that i did not handle this changes,
because i did not use node_modules to resolve this kind of tasks

P.S. Notes about task -> **"SQLite database should be in the repo too."**

If you run `` make extract `` command, it automatically creates all necessary directories and files:
- tmp
  - db -> where sqlite db exists
  - pdfs -> where pdf files downloaded


### If you dont want to use **Makefile** for some reason then you can run following commands:

1. Specify **GEMINI_API_KEY** inside .env folder. You can also specify **GEMINI_MODEL**

2. You need to install dependencies
    - `` python3 -m venv venv ``
    - `` source venv/bin/activate && pip install -r requirements.txt ``

3. To download pdf-files and extract metadata from them, use:
    - `` PYTHONPATH=. python3 **PROJECT_DIR**/src/scripts/index.py" ``

      **PROJECT_DIR** is root directory path. None that you MUST use **PYTHONPATH=.** for modules resolution

4. To launch FastAPI project run
    - `` uvicorn src.api.app:app --reload --port **API_PORT** ``

      **API_PORT** specify API port

5. To see results run
    - `` python3 -m http.server **HTML_PORT** --directory **PROJECT_DIR**/src/templates/" ``

    **HTML_PORT** specify HTML port

    **PROJECT_DIR** is root directory path