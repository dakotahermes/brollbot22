# 🎬 B-Roll Bot - AI Video Assistant

Transform your video scripts into professional B-roll suggestions using AI. This tool analyzes your script's emotional beats and generates specific prompts for AI video generation or stock footage searches.

## ✨ Features

- **Emotional Scene Analysis**: Breaks down scripts into emotional beats with timestamps
- **AI Generation Prompts**: Creates optimized prompts for tools like Runway, Pika, and Kling
- **Stock Footage Guidance**: Provides search instructions for finding relevant clips
- **Multiple Export Formats**: Download results as CSV or JSON
- **Feasibility Assessment**: Evaluates which scenes are best suited for AI generation
- **Configurable Settings**: Customize duration, aspect ratios, and tones

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone or download the files**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

## 📁 Project Structure

```
├── main.py              # Main Streamlit application
├── agents.py            # AI agent logic for processing scripts
├── models.py            # Pydantic data models
├── config.py            # Configuration and constants
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## 🎯 How It Works

1. **Script Analysis**: The AI analyzes your script to identify emotional beats and key moments
2. **Scene Generation**: Creates vivid scene descriptions that match your content's tone
3. **Feasibility Check**: Evaluates whether each scene can be generated by current AI video tools
4. **Prompt Optimization**: Formats scenes into optimized prompts for video generation
5. **Export Options**: Provides downloadable files for easy integration into your workflow

## 🛠️ Configuration

The app can be configured through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4` | OpenAI model to use |
| `DEFAULT_DURATION` | `5` | Default clip duration in seconds |
| `DEFAULT_ASPECT_RATIO` | `9:16` | Default video aspect ratio |
| `CACHE_TTL` | `3600` | Cache duration in seconds |
| `MAX_SCRIPT_LENGTH` | `5000` | Maximum script character limit |
| `MIN_SCRIPT_LENGTH` | `10` | Minimum script character limit |

## 🎨 Supported Tones

- **Inspiring**: Uplifting, aspirational visuals
- **Urgent**: Dynamic, fast-paced scenes  
- **Calm**: Peaceful, tranquil imagery
- **Funny**: Playful, lighthearted visuals
- **Serious**: Professional, authoritative scenes
- **Emotional**: Heartfelt, touching imagery
- **Uplifting**: Positive, encouraging visuals
- **Mysterious**: Intriguing, enigmatic scenes

## 📋 Supported Formats

- **UGC**: User-generated content style with authentic, relatable visuals
- **Talking Head**: Supporting visuals for presenter-style content
- **Testimonial**: Trust-building imagery for customer testimonials

## 💡 Usage Tips

### For AI Video Generation
- Copy the generation prompts to tools like Runway, Pika, or Kling
- Use the confidence score to prioritize which scenes to generate first
- Adjust duration and aspect ratio based on your needs

### For Stock Footage
- Use the search instructions to find relevant clips
- Look for footage that matches the specified emotional tone
- Consider the timing and placement suggestions

### For Video Editing
- Insert B-roll clips after the specified script excerpts
- Match clip duration to your pacing requirements
- Ensure emotional tone aligns with your narrative

## 🔧 Development

### Adding New Features
The modular structure makes it easy to extend:

- **New tones**: Add to `TONE_GUIDANCE` in `config.py`
- **New formats**: Add to `FORMAT_GUIDANCE` in `config.py`  
- **New models**: Extend Pydantic models in `models.py`
- **New agents**: Add processing logic in `agents.py`

### Testing
```bash
# Install development dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v --cov=.
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)  
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for the GPT-4 API
- Streamlit for the web interface framework
- The AI video generation community for inspiration
