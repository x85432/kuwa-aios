import logging
import gradio as gr
from dotenv import load_dotenv
from src.text_to_cad import text_to_cad

def translate_prompt(prompt, language):
    # Your prompt translation logic here
    # Return the translated prompt
    # Example:
    # translated_prompt = "Translated prompt"
    # return translated_prompt
    return prompt

if __name__ == "__main__":
    load_dotenv()  # take environment variables from .env.
    logging.basicConfig(level=logging.INFO)

    # Create the Gradio interface
    iface = gr.Interface(
        fn=text_to_cad,
        inputs=gr.TextArea(label="Prompt"),
        outputs=gr.Model3D(label="3D Model"),
        title="Text to CAD Model Generator",
        examples=["A dodecahedron", "A 1/2 inch gear with 21 teeth", "Design a gear with 40 teeth", "A 3x6 lego"],
        flagging_mode="never",
        theme=gr.themes.Soft(),
    )

    iface.launch(share=True, server_name='0.0.0.0')

    # # Add a "Translate" button with a dropdown for language selection
    # with iface:
    #     with gr.Row():
    #         language_dropdown = gr.Dropdown(label="Language", choices=["English", "Spanish", "French", "German"], value="English")
    #         translate_button = gr.Button("Translate")

    #     translate_button.click(
    #         fn=translate_prompt,
    #         inputs=[iface.input, language_dropdown],
    #         outputs=[iface.input]
    #     )

    # # Start the interface
    # iface.launch()