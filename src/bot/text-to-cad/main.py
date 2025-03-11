import os
import logging
import argparse
import gradio as gr
from pathlib import Path
from dotenv import load_dotenv
from gradio_i18n import Translate, gettext as _
from src.text_to_cad import text_to_cad


def clear_all():
    return [None, None, gr.DownloadButton(visible=False)]


def translate_prompt(prompt, language):
    # Your prompt translation logic here
    # Return the translated prompt
    # Example:
    # translated_prompt = "Translated prompt"
    # return translated_prompt
    return prompt


def generate_cad_model(prompt):
    file_path = text_to_cad(prompt=prompt)
    name = Path(file_path).name
    yield [
        file_path,
        gr.DownloadButton(
            label=_("Download") + f" {name}", value=file_path, visible=True
        ),
    ]
    os.remove(file_path)


def create_main_ui():
    gr.Markdown(_("# Text to CAD Model Generator"))
    with gr.Row(equal_height=True):
        with gr.Column(scale=1, min_width=300):
            prompt_area = gr.TextArea(label=_("Prompt"))
            with gr.Row():
                clear_btn = gr.Button(_("Clear"))
                translate_btn = gr.Button(_("Translate"), interactive=False)
                generate_btn = gr.Button(_("Generate"), variant="primary")
        with gr.Column(scale=2, min_width=300):
            model_display = gr.Model3D(label=_("3D Model"))
            download_btn = gr.DownloadButton(visible=False)
    gr.Examples(
        label=_("Examples"),
        examples=[
            _("A dodecahedron"),
            _("A 1/2 inch gear with 21 teeth"),
            _("Design a gear with 40 teeth"),
            _("A 3x6 lego"),
            _("一個60齒的齒輪"),
        ],
        inputs=prompt_area,
    )

    clear_btn.click(clear_all, None, [prompt_area, model_display, download_btn])
    translate_btn.click(translate_prompt, prompt_area, prompt_area)
    generate_btn.click(generate_cad_model, prompt_area, [model_display, download_btn])


if __name__ == "__main__":
    load_dotenv()  # take environment variables from .env.
    logging.basicConfig(level=logging.INFO)

    # Create the Gradio interface
    with gr.Blocks(theme=gr.themes.Soft()) as ui:
        lang = gr.Dropdown(
            choices=[("English", "en"), ("中文", "zh")], label=_("Language")
        )
        with Translate("translation.yaml", lang, placeholder_langs=["en", "zh"]):
            create_main_ui()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_name", type=str, default=None, help="Gradio server host"
    )
    parser.add_argument(
        "--server_port", type=int, default=None, help="Gradio server port"
    )
    parser.add_argument("--root_path", type=str, default=None, help="Gradio root path")
    args = parser.parse_args()

    ui.launch(
        server_name=args.server_name,
        server_port=args.server_port,
        root_path=args.root_path,
    )
