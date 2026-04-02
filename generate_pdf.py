from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT = "McKinnons_Chatbot_Overview.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=20*mm,
    leftMargin=20*mm,
    topMargin=20*mm,
    bottomMargin=20*mm,
)

styles = getSampleStyleSheet()

# Custom styles
BRAND = colors.HexColor("#1B3A6B")
ACCENT = colors.HexColor("#2E7D32")
LIGHT_GREY = colors.HexColor("#F5F5F5")
MID_GREY = colors.HexColor("#BDBDBD")

title_style = ParagraphStyle(
    "Title", parent=styles["Normal"],
    fontSize=26, textColor=BRAND, spaceAfter=4,
    fontName="Helvetica-Bold", alignment=TA_CENTER
)
subtitle_style = ParagraphStyle(
    "Subtitle", parent=styles["Normal"],
    fontSize=12, textColor=colors.grey, spaceAfter=16,
    fontName="Helvetica", alignment=TA_CENTER
)
section_style = ParagraphStyle(
    "Section", parent=styles["Normal"],
    fontSize=14, textColor=BRAND, spaceBefore=14, spaceAfter=6,
    fontName="Helvetica-Bold"
)
body_style = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontSize=10, leading=15, spaceAfter=6,
    fontName="Helvetica"
)
caption_style = ParagraphStyle(
    "Caption", parent=styles["Normal"],
    fontSize=9, textColor=colors.grey, spaceAfter=10,
    fontName="Helvetica-Oblique", alignment=TA_CENTER
)

def table(data, col_widths, header=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("FONTNAME",  (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",  (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT_GREY]),
        ("GRID",      (0,0), (-1,-1), 0.4, MID_GREY),
        ("VALIGN",    (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",(0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",(0,0),(-1,-1), 8),
    ]
    if header:
        style += [
            ("BACKGROUND", (0,0), (-1,0), BRAND),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ]
    t.setStyle(TableStyle(style))
    return t

W = 170*mm  # usable width

story = []

# ── Header ────────────────────────────────────────────────────────────────────
story.append(Spacer(1, 8*mm))
story.append(Paragraph("McKinnon's Cruisers", title_style))
story.append(Paragraph("AI Chatbot — How It Works", subtitle_style))
story.append(HRFlowable(width=W, thickness=1.5, color=BRAND, spaceAfter=10))

# ── Overview ─────────────────────────────────────────────────────────────────
story.append(Paragraph("Overview", section_style))
story.append(Paragraph(
    "The McKinnon's Cruisers chatbot is a customer service assistant that answers questions "
    "about your products, parts, and builds. It works entirely from your own website content — "
    "no external databases, no third-party data sources. Customers get instant, accurate answers "
    "24/7 without needing to call or email.",
    body_style
))

# ── How It Works ──────────────────────────────────────────────────────────────
story.append(Paragraph("How It Works", section_style))
story.append(Paragraph(
    "The system has two stages: a one-time setup, and the live conversation loop.",
    body_style
))

story.append(Spacer(1, 3*mm))
story.append(Paragraph("Stage 1 — Setup (run once)", ParagraphStyle(
    "SH", parent=body_style, fontName="Helvetica-Bold", textColor=ACCENT)))
step_data = [
    ["Step", "What Happens"],
    ["1. Scrape",  "A script visits every page on mckinnonscruisers.com and saves all the text to a file on your computer."],
    ["2. Store",   "The text is saved locally as website_content.txt. No external database is needed."],
    ["3. Ready",   "The chatbot app is started and loads this file into memory. Setup is complete."],
]
story.append(table(step_data, [25*mm, 145*mm]))

story.append(Spacer(1, 5*mm))
story.append(Paragraph("Stage 2 — Every Customer Conversation", ParagraphStyle(
    "SH2", parent=body_style, fontName="Helvetica-Bold", textColor=ACCENT)))
conv_data = [
    ["Step", "What Happens"],
    ["1. Customer asks",   "The customer types a question into the chat interface in their browser."],
    ["2. Find relevant pages", "The app searches your saved website content for the pages most relevant to the question."],
    ["3. Send to Claude", "The relevant pages and the question are sent securely to Claude (Anthropic's AI)."],
    ["4. Generate answer", "Claude reads the content and writes a helpful, natural-language reply."],
    ["5. Display reply",  "The answer is shown to the customer in the chat window."],
]
story.append(table(conv_data, [40*mm, 130*mm]))

story.append(Spacer(1, 2*mm))
story.append(Paragraph(
    "Only the pages relevant to each question are sent — not the entire website — "
    "which keeps responses fast and costs low.",
    caption_style
))

# ── Components ────────────────────────────────────────────────────────────────
story.append(Paragraph("System Components", section_style))
comp_data = [
    ["Component",          "What It Is",          "Role"],
    ["Scraper",            "Python script",        "Reads your website and saves the text. Re-run whenever your site is updated."],
    ["website_content.txt","Text file",            "Stores all website content locally on your computer. No external database."],
    ["Streamlit App",      "Python web app",       "The chat interface your customers see and interact with."],
    ["Claude API",         "Anthropic AI service", "Reads the relevant content and generates accurate, friendly answers."],
]
story.append(table(comp_data, [38*mm, 35*mm, 97*mm]))

# ── Security & Privacy ────────────────────────────────────────────────────────
story.append(Paragraph("Security & Privacy", section_style))
sec_data = [
    ["Topic",                "Details"],
    ["Customer messages",    "Not stored anywhere. Each conversation lives only in the browser tab and is gone when the tab is closed."],
    ["Your website data",    "Only publicly visible text from your website is used — the same content anyone can read by visiting the site."],
    ["API key security",     "Stored only in a private file on your server. Never sent to the browser or exposed publicly."],
    ["Access control",       "Only people with the link to the chatbot can use it."],
    ["Anthropic privacy",    "Anthropic does not use API conversations to train their AI models by default."],
    ["Data location",        "No customer data is stored. Only the question + relevant website text leaves your machine, sent securely to Anthropic to generate a response."],
]
story.append(table(sec_data, [45*mm, 125*mm]))

# ── Costs ─────────────────────────────────────────────────────────────────────
story.append(Paragraph("Running Costs", section_style))
story.append(Paragraph(
    "The chatbot uses the Claude Haiku AI model, which is one of the most cost-effective "
    "AI models available. Costs are based only on usage — there is no monthly subscription.",
    body_style
))
cost_data = [
    ["Usage Level",         "Approx. Monthly Cost", "Notes"],
    ["Low (100 questions)",   "~$0.10",             "Very light usage"],
    ["Medium (500 questions)","~$0.50",             "Regular daily use"],
    ["High (2,000 questions)","~$2.00",             "Busy periods"],
]
story.append(table(cost_data, [55*mm, 50*mm, 65*mm]))
story.append(Paragraph(
    "Costs are billed directly by Anthropic. You can set a monthly spending limit in your Anthropic account.",
    caption_style
))

# ── Maintenance ───────────────────────────────────────────────────────────────
story.append(Paragraph("Keeping It Up to Date", section_style))
maint_data = [
    ["Task",                        "How Often",      "What to Do"],
    ["Update website content",      "When site changes", "Re-run the scraper script (takes ~2 minutes)."],
    ["Monitor costs",               "Monthly",        "Check usage in your Anthropic account dashboard."],
    ["Restart chatbot (if needed)", "As required",    "Run one command to restart the app."],
]
story.append(table(maint_data, [60*mm, 35*mm, 75*mm]))

# ── Footer ────────────────────────────────────────────────────────────────────
story.append(Spacer(1, 8*mm))
story.append(HRFlowable(width=W, thickness=0.8, color=MID_GREY, spaceAfter=6))
story.append(Paragraph(
    "For questions about this system, contact your developer.",
    caption_style
))

doc.build(story)
print(f"PDF created: {OUTPUT}")
