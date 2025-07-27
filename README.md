# AnalyzeTheChat

AnalyzeTheChat is a Streamlit-based web application that allows you to analyze WhatsApp chat exports for message patterns, top participants, and more. This tool is especially useful for visualizing group dynamics and understanding communication behavior.

---

## 🌐 Live Demo
- Check out Live Demo: https://analyzethechat.up.railway.app/
- Analyze your individual & groups chats
---

## 📚 Features

* ✅ Upload WhatsApp `.txt` chat exports
* 🕰️ Generate word clouds of most frequent words
* 📊 View message activity over time (daily, monthly)
* 📊 Top senders, emojis, links
* 🙋 Group vs Individual analysis
* 🔮 Remove stop words automatically
* ⚡ Simple and intuitive Streamlit UI

---

## 📁 Folder Structure

```
WHATSAPP-CHAT-ANALYSIS/
├── .streamlit/              # Streamlit configuration
├── venv/                    # Virtual environment (ignored)
├── app.py                   # Main Streamlit app file
├── debug.ipynb              # Notebook for testing/debugging
├── preprocessor.py          # Chat preprocessing logic
├── utils.py                 # Helper functions
├── stop_words.txt           # Custom stop words list
├── requirements.txt         # Required Python packages
├── .gitignore               # Files and folders to ignore in Git
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/adeelHassan123/AnalyzeTheChat.git
cd AnalyzeTheChat
```

### 2. Set up Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run app.py
```

---

## 📂 How to Use

1. Export a WhatsApp chat as `.txt` file
2. Open the web app in your browser
3. Upload the chat file
4. View analysis: messages per user, most used words, emoji usage, timelines, etc.

---

## 📄 Example

To export your WhatsApp chat:

* Open the chat on WhatsApp
* Tap on the 3-dot menu → More → Export chat
* Choose **Without media** and send to yourself
* Save the `.txt` file and upload it to this app

---

## 💡 Technologies Used

* Python
* Streamlit
* Pandas
* Numpy
* Matplotlib / Seaborn
* Regular Expressions

---

## 🌟 Contributions

Feel free to fork this repository and submit pull requests. Suggestions and issues are welcome!

---

## ⚠️ License

This project is open source under the MIT License.

---

## 🚀 Future Improvements

* Add sentiment analysis
* Export visualizations as images
* Support Telegram/other platforms
* Add login and chat memory

---

## 🙏 Acknowledgements

This project is developed as a learning tool for data analysis, visualization, and Streamlit apps. Inspired by common needs of WhatsApp data insights.
