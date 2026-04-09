# Streamlit Chat Interface

A ChatGPT-like interface built with Streamlit for your project.

This frontend is now wired to your `infosys` backend folder.

## Run locally

1. Create and activate your Python environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install -r infosys/requirements.txt
   pip install -e ./infosys
   ```

3. Start the app:

   ```bash
   streamlit run app.py
   ```

If you still see import errors, run Streamlit with the same Python used for installs:

```bash
C:/Users/shino/AppData/Local/Programs/Python/Python313/python.exe -m streamlit run app.py
```

## Customize

- Open `app.py`
- The app auto-loads backend code from `infosys/src`.
- In the sidebar, choose mode:
   - `Quick Answer` -> calls `opendeepresearcher.main.ask()`
   - `Deep Research` -> calls `opendeepresearcher.main.run()`

## Folder Linking Notes

- Keep this structure:

   ```text
   in/
   ├─ app.py
   └─ infosys/
       └─ src/opendeepresearcher/
   ```

- If import fails in the app, reinstall editable package:

   ```bash
   pip install -e ./infosys
   ```
