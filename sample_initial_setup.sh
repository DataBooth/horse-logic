pdm add streamlit watchdog
pdm add pandas
pdm add --dev notebook

pdm export --o requirements.txt --without-hashes --prod

streamlit --version > .streamlit/version_info.md && streamlit config show > .streamlit/config.toml