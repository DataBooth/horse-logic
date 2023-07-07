# Appendix: Template info

`ST-TEMPLATE` - Base template / project structure for a DataBooth data app.

## Getting Started - Initial Setup / How to reproduce

1. Based on this template repository. https://github.com/DataBooth/st-template.git
2. Initialise the PDM package/environment manager (see [README_pdm.md](README_pdm.md))
3. Activate the venv i.e. `source .venv/bin/activate`
4. Add the required package dependencies (see [README_pdm.md](README_pdm.md))

### Streamlit app

If creating a Streamlit app, the following steps are required:
- Create/update the Streamlit configuration file (see [.streamlit/README_streamlit_config.md](.streamlit/README_streamlit_config.md)). Note that the Streamlit [.streamlit/config.toml](.streamlit/config.toml) file can change between versions.
- Ensure the template application works, run it via `streamlit run src/AppName.py`

*Note that the shell script [sample_initial_setup.sh](sample_initial_setup.sh) contains an example of the typical commands to implement steps 4-6 above.*

## Data Analysis / Exploration

- Exploratory data analysis can be performed by creating Jupyter notebooks in the [notebooks](notebooks) folder.

### TODOs

Add info on pre-commit install setup (`pre-commit install`) and making changes to `.pre-commit-config.yaml`.
