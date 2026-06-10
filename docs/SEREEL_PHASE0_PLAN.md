# Sereel Content Engine — Phase 0 Runbook

**Audience:** Aishat (operator), with setup support from Bunny  
**Goal of this phase:** Prove MoneyPrinterTurbo is useful and the output is good enough to represent Sereel, before we spend anything on engineering or hosting.  
**Owner of this phase:** *[assign a name before starting]*  
**Status:** Phase 0 (local, free, no custom code)

---

## 1. What Phase 0 is, and what it is not

Phase 0 is a validation step. We are not building a product yet. We are running MoneyPrinterTurbo as-is on Aishat's laptop to answer one question:

> Is the output good enough to put on Sereel's social channels, and is the topic-to-video workflow actually useful day to day?

If the answer is yes, we move to Phase 1 (Docker hardening, brand templates, review process) and later Phase 2 (hosted internal web app at a Sereel subdomain). If the answer is no, we stop here having spent nothing.

**In scope for Phase 0**
- Running the tool locally via Docker
- Generating videos from topics and key points
- Using Sereel's own brand visuals instead of generic stock footage
- A manual content review step before anything is published

**Out of scope for Phase 0** (do not attempt yet)
- Hosting on a server or subdomain
- A custom Sereel-branded frontend
- Automated publishing to YouTube, Instagram, or TikTok
- AI image generation inside the pipeline
- Multiple people using it at once

---

## 2. Mental model

MoneyPrinterTurbo is an assembly engine, not a creative director. Given a topic, it asks an LLM to write a short script, generates a voiceover, creates synced subtitles, gathers visuals, adds background music, and renders a finished vertical MP4.

It does not have taste. The quality of the output is set by the quality of the inputs: the script, the visuals we supply, and the human who reviews it before publishing. Treat the tool as the part that saves time on rendering, not the part that decides whether something is good.

The licence is MIT, so we are free to run, modify, and fork it internally.

---

## 3. Prerequisites

### Hardware check
| Item | Minimum | Comfortable |
|------|---------|-------------|
| RAM | 8 GB | 16 GB |
| CPU | 4 cores | 6 to 8 cores |
| Free disk | 10 GB | 30 GB or more |

Video files accumulate quickly. Keep an eye on disk space and clear old outputs.

A GPU is **not** required for our setup, because we keep the heavy work in the cloud (see config below).

### Software
1. **Docker Desktop.** Install from https://www.docker.com/products/docker-desktop/ . This is the only thing Aishat needs to install. It removes all the Python and dependency setup.
2. A **terminal**. On Mac this is the Terminal app. On Windows, use the WSL terminal that Docker Desktop sets up.

### Accounts and API keys (provision these before handing the tool to Aishat)
These should be created by the team and pasted in for her, not hunted down by her.

- **Pexels API key** (free): https://www.pexels.com/api/ . Used for stock footage fallback. We will mostly use our own visuals, but the tool still expects a media source configured.
- **LLM provider key.** Recommend **DeepSeek** for low cost. The tool also supports OpenAI, Gemini, Qwen, Moonshot, and others. One key for one provider is enough.

> Voice (TTS) needs no key. The default is Edge TTS, which is free. In the interface it appears as "Azure TTS V1". Leave it as is for Phase 0.

---

## 4. Setup

Run these in the terminal. Pick a folder path with **no spaces, no accents, no non-English characters**. This is a hard requirement of the tool. A path like `~/sereel/content-engine` is good. A path like `~/Aishat's Folder/Sereel 视频` will break it.

```bash
# 1. Get the code
git clone https://github.com/harry0703/MoneyPrinterTurbo.git
cd MoneyPrinterTurbo

# 2. Create the config file from the Sereel template
cp config.sereel.toml config.toml

# 3. Edit config.toml — paste in the API keys (see section 5), then start
docker compose up
```

The first run downloads the Docker image and will take several minutes. Later runs are fast.

When it is running, open a browser (Chrome or Edge work best) and go to:

- **Web interface:** http://127.0.0.1:8501

If the page is blank, switch to Chrome or Edge and reload.

To stop the tool, go back to the terminal and press `Ctrl + C`.

---

## 5. Config file (`config.toml`)

Open `config.toml` in any text editor. You only need to set a few things for Phase 0.

- `llm_provider` — already set to `deepseek` in `config.sereel.toml`. Fill in `deepseek_api_key`.
- `pexels_api_keys` — paste the Pexels key here.
- `subtitle_provider` — already set to `edge`. It is fast and needs no GPU. Do not use `whisper` in Phase 0; it requires a 3 GB model download.

Leave everything else at default. The voice can also be changed later from the web interface, so no need to touch it in the file.

Save the file. If the tool is already running, stop it (`Ctrl + C`) and run `docker compose up` again so it picks up the changes.

---

## 6. Using Sereel's own visuals (the important part)

By default the tool pulls generic stock clips from Pexels. That is exactly the look we want to avoid, because it is the same footage every crypto content farm uses. The fix is to feed it our own material.

The tool supports a **Local file** source in the web UI. Instead of searching Pexels, it will use video clips and images you upload directly in the browser.

**Workflow for Aishat:**
1. Collect the visuals for a video into a folder on your laptop. These can be:
   - Sereel product screenshots
   - Charts and diagrams
   - Brand graphics and short clips
   - AI-generated images made elsewhere (Midjourney, DALL-E, etc.) if needed
2. In the web interface, find the **Video Source** setting and change it from Pexels to **Local file**.
3. Use the file uploader that appears to select your visuals. Supported formats: `mp4`, `mov`, `avi`, `flv`, `mkv`, `jpg`, `jpeg`, `png`.
4. Generate. The tool now assembles your supplied visuals instead of stock footage.

> **Note:** The uploaded files are saved to `./storage/local_videos/` inside the project folder and persist across generations as long as you don't re-upload new files.

**Guidance on visuals:** for Sereel, real product and data visuals beat generated stock-style images almost every time. A clean chart or a real screen of the marketplace looks like a company with a product. A generated illustration of a glowing coin looks like everyone else. Lead with the real thing.

The tool will never generate images for you in Phase 0. Aishat creates or selects them and uploads them in the UI. That is by design for now.

---

## 6b. Keyword-triggered image overlays (optional)

In addition to the main visuals, you can configure **keyword overlays** — images that fade in smoothly whenever a specific word is spoken in the narration. This is useful for reinforcing concepts visually: when the narrator says "Ethereum," an Ethereum logo pops up; when "stablecoin" is mentioned, a stablecoin icon appears.

**How it works:**
- The tool scans the subtitle text for configured keywords
- When a keyword is found, the matching image fades in at that exact moment
- The image stays visible for a few seconds, then fades out
- Each keyword only triggers once per video (first match wins)

**Setup:**
1. Place your overlay images in `resource/overlays/` (create the folder if needed). PNG with transparency works best.
2. Open `config.toml` and add a `[keyword_overlay]` section:

```toml
[keyword_overlay]
enabled = true
fade_duration = 0.6        # seconds to fade in/out
display_duration = 3.0     # how long the image stays visible
image_size = 180           # width in pixels
position = "center"        # options: center, top, bottom, top-right, top-left

[[keyword_overlay.images]]
keyword = "ethereum"
path = "resource/overlays/ethereum.png"

[[keyword_overlay.images]]
keyword = "stablecoin"
path = "resource/overlays/stablecoin.png"

[[keyword_overlay.images]]
keyword = "africa"
path = "resource/overlays/africa-map.png"
```

3. Restart the tool (`Ctrl + C` then `docker compose up`) to pick up the changes.

**Position options:**
| Value | Placement |
|-------|-----------|
| `center` | Center of screen |
| `top` | Horizontally centered, upper third |
| `bottom` | Horizontally centered, lower third (above subtitles) |
| `top-right` | Top right corner |
| `top-left` | Top left corner |

The overlay sits above the video and subtitles but below the Sereel logo. Transparent PNGs are fully supported.

---

## 7. Generating a video

1. Enter a **topic** and the **key points** you want covered.
2. Choose the format. For Shorts, Reels, and TikTok use **vertical 9:16 (1080x1920)**. This one format covers all three platforms.
3. Set the video source to **Local file** and upload your visuals (section 6).
4. Generate. Rendering takes anywhere from about a minute to several minutes depending on length and the laptop.
5. Preview the result. Download the MP4 if it passes review (section 8).

Use batch generation if you want a few variations of the same topic to pick from.

---

## 8. Content review rule (do not skip)

The tool writes scripts with an LLM. It has no idea what is true and no idea what is regulated. Every video passes through the same human review the rest of Sereel's marketing does, before it is published.

Two tiers:

- **Education content** (what tokenization is, how RWAs work, why African capital markets need new rails): low risk. Normal review.
- **Anything naming a specific asset, yield, or return, or anything that nudges a viewer toward investing on the Sereel marketplace:** this is regulated financial promotion. A human must sign off before it goes live. No exceptions. We operate in a CMA sandbox and this is exactly the kind of thing that gets scrutiny.

In Phase 0 this gate is a rule, not software. We build it into the product itself in a later phase. For now, the rule is: nothing publishes without review.

---

## 9. Troubleshooting

**"No ffmpeg exe could be found"**
Normally ffmpeg downloads automatically. If it fails, the Docker setup usually avoids this entirely, which is one reason we use Docker. If it persists, flag Bunny.

**Blank browser page at 127.0.0.1:8501**
Switch to Chrome or Edge and reload.

**"Too many open files" (Mac or Linux)**
In the terminal, raise the limit with `ulimit -n 10240`, then restart the tool.

**Tool will not start after editing config**
Check that `config.toml` has no typos and that the path you cloned into has no spaces or special characters. Stop with `Ctrl + C` and run `docker compose up` again.

**"no valid materials found" when using Local file**
Make sure every uploaded file is at least 480×480 pixels. The tool rejects low-resolution materials. Also check that the file format is supported.

**Anything else**
Capture the error text and send it to Bunny. Do not spend more than a few minutes stuck; the point of Phase 0 is to learn fast, not to debug.

---

## 10. Phase 0 exit criteria

We move to Phase 1 only when all of these are true:

1. Aishat can generate a video end to end without help.
2. At least one batch of around ten videos has been produced on real Sereel topics.
3. The output, using our own visuals, clears the bar of "we would be comfortable a bank partner sees this."
4. Aishat finds the workflow genuinely useful, not a chore.

If the visuals or workflow do not clear that bar, we stop and reconsider rather than building further on a weak base.

---

## 11. What comes after (for context only, not for now)

- **Phase 1:** locked brand templates (fonts, colours, intro and outro), a written process, review step formalised.
- **Phase 2:** thin Sereel-branded web app, hosted on a cheap server at a password-gated subdomain such as `studio.sereel.com`, with the financial-promotion approval gate built into the software.
- **Phase 3:** AI image generation wired into the pipeline, and automated publishing to the platforms via their APIs. Significant engineering and ongoing maintenance. Only if volume justifies it.

A note that matters: if this becomes a real tool, someone has to own keeping it alive. Forks of open-source projects rot when nobody maintains them. Decide who owns it before Phase 2.
