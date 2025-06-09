import reflex as rx


def get_color_classes(
    color: rx.Var[str],
) -> tuple[rx.Var[str], rx.Var[str]]:
    """Returns Tailwind CSS classes for a given color."""
    on_class = rx.match(
        color,
        (
            "yellow",
            "bg-yellow-400 shadow-lg shadow-yellow-400/50",
        ),
        (
            "blue",
            "bg-blue-500 shadow-lg shadow-blue-500/50",
        ),
        (
            "green",
            "bg-green-500 shadow-lg shadow-green-500/50",
        ),
        "bg-gray-500",
    )
    button_class = rx.match(
        color,
        ("yellow", "bg-yellow-500 hover:bg-yellow-600"),
        ("blue", "bg-blue-600 hover:bg-blue-700"),
        ("green", "bg-green-600 hover:bg-green-700"),
        "bg-gray-600 hover:bg-gray-700",
    )
    return (on_class, button_class)


def led_controller(led: dict) -> rx.Component:
    """A component to control a single LED."""
    on_class, button_class = get_color_classes(led["color"])
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                class_name=rx.cond(
                    led["status"],
                    on_class,
                    "bg-gray-300 h-6 w-6 rounded-full transition-all",
                )
            ),
            rx.el.p(
                f"{led['color'].to(str).capitalize()} LED: ",
                rx.el.span(
                    rx.cond(led["status"], "ON", "OFF"),
                    class_name=rx.cond(
                        led["status"],
                        "text-green-600 font-bold",
                        "text-red-600 font-bold",
                    ),
                ),
                class_name="text-lg font-medium text-gray-700 capitalize",
            ),
            class_name="flex items-center gap-4",
        ),
        rx.el.button(
            rx.cond(led["status"], "Turn OFF", "Turn ON"),
            on_click=lambda: LedState.toggle_led(led["id"]),
            disabled=LedState.is_loading,
            class_name=rx.cond(
                LedState.is_loading,
                "w-28 py-2 px-4 text-white font-semibold rounded-lg shadow-md transition-transform transform bg-gray-400 cursor-not-allowed",
                f"w-28 py-2 px-4 text-white font-semibold rounded-lg shadow-md transition-transform transform hover:scale-105 {button_class}",
            ),
        ),
        class_name="flex items-center justify-between p-4 bg-gray-50 rounded-lg w-full",
    )


def esp32_setup_info() -> rx.Component:
    """A component to display information about the required ESP32 setup."""
    return rx.el.div(
        rx.el.h3(
            "ESP32 Setup Guide",
            class_name="text-lg font-semibold text-gray-700",
        ),
        rx.el.p(
            "For this to work, your ESP32 must be connected to the same WiFi network and run a web server with the following endpoints for each LED color (yellow, blue, green):",
            class_name="text-sm text-gray-600 mt-2",
        ),
        rx.el.ul(
            rx.el.li(
                rx.el.code("/led/{color}/on"),
                " - to turn the specific LED on.",
                class_name="mt-1",
            ),
            rx.el.li(
                rx.el.code("/led/{color}/off"),
                " - to turn the specific LED off.",
                class_name="mt-1",
            ),
            class_name="list-disc list-inside bg-gray-100 p-3 rounded-lg mt-2 text-sm",
        ),
        class_name="mt-8 p-4 border border-gray-200 rounded-xl bg-white w-full max-w-md",
    )


def index() -> rx.Component:
    """The main page of the app."""
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.icon(
                    tag="lightbulb",
                    class_name="h-12 w-12 text-yellow-400",
                ),
                rx.el.h1(
                    "ESP32 LED Controller",
                    class_name="text-3xl font-bold text-gray-800",
                ),
                class_name="flex items-center gap-4 mb-8",
            ),
            rx.el.div(
                rx.el.label(
                    "ESP32 IP Address:",
                    class_name="font-medium text-gray-700",
                ),
                rx.el.input(
                    default_value=LedState.esp32_ip,
                    on_change=LedState.set_esp32_ip.debounce(
                        500
                    ),
                    placeholder="e.g., 192.168.1.100",
                    class_name="mt-2 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                ),
                class_name="mb-6 w-full",
            ),
            rx.el.div(
                rx.foreach(LedState.leds, led_controller),
                class_name="flex flex-col gap-4 w-full",
            ),
            rx.cond(
                LedState.is_loading,
                rx.el.div(
                    rx.spinner(class_name="text-blue-500"),
                    rx.el.p(
                        "Sending command...",
                        class_name="text-gray-500 ml-2",
                    ),
                    class_name="flex items-center justify-center mt-4",
                ),
                rx.el.div(class_name="h-10 mt-4"),
            ),
            esp32_setup_info(),
            class_name="bg-white p-8 rounded-2xl shadow-xl border border-gray-100 flex flex-col items-center max-w-md w-full",
        ),
        class_name="flex items-center justify-center min-h-screen bg-gray-100 font-['Inter']",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(
            rel="preconnect",
            href="https://fonts.googleapis.com",
        ),
        rx.el.link(
            rel="preconnect",
            href="https://fonts.gstatic.com",
            crossorigin="",
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
            rel="stylesheet",
        ),
    ],
)



import requests
import asyncio
from typing import TypedDict


class Led(TypedDict):
    id: int
    color: str
    status: bool


class LedState(rx.State):
    """Manages the state of the LEDs and communication with the ESP32."""

    leds: list[Led] = [
        {"id": 0, "color": "yellow", "status": False},
        {"id": 1, "color": "blue", "status": False},
        {"id": 2, "color": "green", "status": False},
    ]
    is_loading: bool = False
    esp32_ip: str = "192.168.1.100"
    error_message: str = ""

    def _get_led_by_id(
        self, led_id: int
    ) -> tuple[int, Led | None]:
        """Finds an LED and its index in the state list by its ID."""
        for i, led in enumerate(self.leds):
            if led["id"] == led_id:
                return (i, led)
        return (-1, None)

    @rx.event(background=True)
    async def toggle_led(self, led_id: int):
        """Toggles a specific LED's state by sending a request to the ESP32."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        led_index, led = self._get_led_by_id(led_id)
        if led is None:
            async with self:
                self.error_message = (
                    f"Invalid LED ID: {led_id}"
                )
                yield rx.toast(
                    self.error_message, duration=3000
                )
                self.is_loading = False
            return
        target_state = "on" if not led["status"] else "off"
        url = f"http://{self.esp32_ip}/led/{led['color']}/{target_state}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            async with self:
                idx_to_update, _ = self._get_led_by_id(
                    led_id
                )
                if idx_to_update != -1:
                    self.leds[idx_to_update]["status"] = (
                        not self.leds[idx_to_update][
                            "status"
                        ]
                    )
        except requests.exceptions.RequestException:
            async with self:
                self.error_message = "Error connecting to ESP32. Check IP and network."
                yield rx.toast(
                    self.error_message, duration=5000
                )
        finally:
            async with self:
                self.is_loading = False





app.add_page(index, route="/")

