# Grafana dashboard panel JSON generator

This script allows you to edit the Grafana panel by adding new port IDs and changing their labels, generating color gradients, and total fields.

## Installation

1. Make sure you have Python 3.X.X installed.fff

2. Clone the repository:

   ```bash
   git clone https://github.com/Yoshintame/grafana-dashbord-panel-generator.git
   ```

3. Navigate to the project directory:

   ```bash
   cd grafana-dashbord-panel-generator
   ```

4. Install the dependencies from the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

   This command will install all the required packages and their versions specified in the `requirements.txt` file. This command need root privileges or `--user` flag.

## Environment Variables

Open the `.env` file and add the required environment variables in the format `KEY=VALUE`. Required environment variables:
- `GRAFANA_API_BASE_URL` - Grafana api token
- `GRAFANA_API_BASE_URL`- Grafana api base url. For example: https://eye.reconn.ru/api
- `MON_BASE_URL` - Observium api base url. For example: https://mon.reconn.local/api/v0
- `MON_AUTH_LOGIN` - Observium authentication login
- `MON_AUTH_PASSWORD` - Observium authentication password

## Commands

The script has two commands:

- `config` with `--url` flag - this command will generate a `config.json` file and backup the initial Grafana panel JSON file, received at the specified url.
- `panel` - this command will apply config to the initial Grafana panel JSON file and generate a new Grafana panel JSON file

## Usage

1. Copy the Grafana panel url, that looks like this:
   https://eye.reconn.ru/d/JkuONx-Vk1/dc-2?orgId=1&refresh=1m&viewPanel=21.
   You can get it from `View` panel.
2. Paste url to following command:

   ```bash
   python main.py config -u "{grafana_panel_url}"
   ```

   Execution this command will generate two files: `config.json` with all existing fields in the panel, their labels and Obesrvium IDs, and `initial-panel-data-ID.json` with initial panel settings.
3. Edit the config file by adding new ports or changing existing ones. You can also change the gradient colors to one of the following options: BLUE, GREEN, PURPLE, ORANGE, or to any [MathPlotLib colormap name](https://matplotlib.org/stable/tutorials/colors/colormaps.html#lightness-of-matplotlib-colormaps).
4. Save the config file and run the following command:

   ```bash
   python main.py panel
   ```

   This will generate the new Grafana panel JSON file. If the label is set to null, an attempt will be made to generate the label from the Observium API.
5. Copy the JSON and paste it into Grafana -&gt; Panel -&gt; Inspect -&gt; Panel JSON.

## Create custom colormap

In `/src/color_sets.json` you can see custom colormaps configurations.
To create new one add this into json:

```json
  "{color_map_name}": [
    {colors_array}
  ],
```

Where `color_map_name` is name of new custom color map and `colors array` is array of HEX colors that defines the gradient. The minimum number of colors is limited to two (the beginning and end of the gradient), the maximum number of colors is not limited.

## TODO

- [x] Custom colormaps
- [x] MathPlotLib colormaps
- [ ] Yaml configuration file
- [ ] Offset colors in custom color maps definition
- [ ] detection of the current color map of the Grafana panel