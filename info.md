# Data scrapper for Crafty Controller
Adds multiple sensors, button with information/statistics/functions grabbed from Crafty Controller account

## Installation

### Requirements:

1. Install this component by copying [these files](https://github.com/Makhuta/homeassistant-crafty_controller/tree/main/custom_components/crafty_controller) to `custom_components/crafty_controller/`.
2. **You will need to restart after installation for the component to start working.**

### Adding new device

To add the **HoneyGain Scrapper** integration to your Home Assistant, use this My button:

<a href="https://my.home-assistant.io/redirect/config_flow_start?domain=crafty_controller" class="my badge" target="_blank"><img src="https://my.home-assistant.io/badges/config_flow_start.svg"></a>

<details><summary style="list-style: none"><h3><b style="cursor: pointer">Manual configuration steps</b></h3></summary>

If the above My button doesn’t work, you can also perform the following steps manually:

- Browse to your Home Assistant instance.

- Go to [Settings > Devices & Services](https://my.home-assistant.io/redirect/integrations/).

- In the bottom right corner, select the [Add Integration button.](https://my.home-assistant.io/redirect/config_flow_start?domain=crafty_controller)

- From the list, select **HoneyGain Scrapper**.

- Follow the instructions on screen to complete the setup.

</details>

## None

The users will be viewed from the JWT token point of view meaning that you might not see some datas when parsing other users with the same token.