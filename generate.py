import torch
from diffusers import (
    StableDiffusionXLPipeline, 
    EulerAncestralDiscreteScheduler,
    AutoencoderKL
)
import os
import argparse
import time

def parse_arguments():
    parser = argparse.ArgumentParser(description='Test on finetune LLaMA model on hate speech and knowledge to generate counter narratives.')
    parser.add_argument('-s', '--single_attempt', action='store_true', default=False, help='generate one time')
    parser.add_argument('-m', '--multiple_attempt',action='store_true', default=False, help='generate multiple times')
    parser.add_argument('-t', '--times', type=int, default=10, help='set generation times for multiple generation, only used when -m set to True')
    parser.add_argument('-o', '--output_dir', type=str, default='output', help='set the output folder to save the image, used for both single and multiple attempt')
    parser.add_argument('-p', '--prompt', type=str, default="1girl, arima kana, oshi no ko, solo, upper body, v, smile, looking at viewer, outdoors, night", help='set prompt for generation, used both in single and multiple generation, make sure to put the text in double quotes')
    parser.add_argument('-n', '--negative_prompt', type=str, default="nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name", help='set negative prompt for generation, used both in single and multiple generation, make sure to put the text in double quotes')
    return parser.parse_args()

def init():
    # Load VAE component
    vae = AutoencoderKL.from_pretrained(
        "madebyollin/sdxl-vae-fp16-fix", 
        torch_dtype=torch.float16
    )

    # Configure the pipeline
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "Linaqruf/animagine-xl-3.0", 
        vae=vae,
        torch_dtype=torch.float16, 
        use_safetensors=True, 
    )
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.to('cuda')
    return pipe

def generate_image(pipe, prompt, negative_prompt, output_path):

    image = pipe(
        prompt, 
        negative_prompt=negative_prompt, 
        width=832,
        height=1216,
        guidance_scale=7,
        num_inference_steps=28
    ).images[0]

    image.save(output_path)

def main():
    pipe = init()
    args = parse_arguments()
    key_prompt = args.prompt.split(',')
    key = key_prompt[0].strip()+'-'+key_prompt[1].strip()+'-' if len(key_prompt)>=2 else ''
    path = os.path.join(args.output_dir, key+str(int(time.time())%100000))
    print("Generate picture to path: "+path)
    if not os.path.exists(path):
        os.makedirs(path)
        print("Automatically create folder.")
    if args.single_attempt:
        generate_image(pipe, args.prompt, args.negative_prompt, os.path.join(path, "output.jpg"))
    elif args.multiple_attempt:
        for idx in range(args.times):
            generate_image(pipe, args.prompt, args.negative_prompt, os.path.join(path, str(idx+1)+".jpg"))
    else:
        print("ERROR, please provide single or multiple attempt flag!")

if __name__ == "__main__":
    main()