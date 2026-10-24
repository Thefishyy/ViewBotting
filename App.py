import streamlit as st
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Page configurations and UI Theme setup
st.set_page_config(
    page_title="Dynamic Proxy Traffic Control", 
    page_icon="🌐",
    layout="wide"
)

# Custom CSS for UI polish
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 1200px; }
    div.stButton > button:first-child { width: 100%; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🌐 Live-Scraping Proxy Traffic Control")
st.markdown("This dashboard automatically scrapes fresh, active public HTTP proxies from open mirrors right before executing requests.")
st.divider()

# Helper function to scrape live public proxies
def fetch_fresh_proxies():
    # URL pointing directly to verified plain text HTTP lists updated continuously
    url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Parse text into clean list elements while filtering out blank lines
            raw_proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
            return raw_proxies
        else:
            return []
    except Exception:
        return []

# Sidebar configuration matrix
with st.sidebar:
    st.header("⚙️ Configuration Settings")
    url = st.text_input("Target Destination URL", placeholder="example.com").strip()
    
    st.subheader("⏱️ Worker Lifespans")
    min_duration = st.number_input("Minimum Duration (sec)", min_value=1, value=5)
    max_duration = st.number_input("Maximum Duration (sec)", min_value=1, value=15)
    
    st.subheader("🤖 Fleet Parameters")
    total_runs = st.slider("Total Workers to Deploy", min_value=1, max_value=50, value=6)
    
    launch_btn = st.button("🚀 Launch Campaign", type="primary")

# Main Interface Analytics Indicators
col_m1, col_m2, col_m3 = st.columns(3)
metric_workers = col_m1.metric("Active Progress", "0 / 0", "Pending")
metric_time = col_m2.metric("Total Engagement Time", "0s", "0s avg")
metric_status = col_m3.metric("System Condition", "Idle", delta=None)

progress_bar = st.progress(0.0)
st.subheader("📜 Real-Time Process Monitor Logs")
log_box = st.code("System ready. Configure constraints and hit deploy.", language="text")

if launch_btn:
    if not url:
        st.error("❌ Action Blocked: A valid destination domain or URL input is required.")
    else:
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
            
        if min_duration > max_duration:
            min_duration, max_duration = max_duration, min_duration

        log_messages = ["[System initialization started...]"]
        log_messages.append("[Fetching fresh live proxies from open-source repository mirrors...]")
        log_box.code("\n".join(log_messages), language="text")
        metric_status.metric("System Condition", "Scraping Proxies...", delta="Active")

        # Execute dynamic generation loop
        proxy_list = fetch_fresh_proxies()
        
        if not proxy_list:
            st.error("❌ Failed to auto-generate proxies. Check your internet connection or repository state.")
            metric_status.metric("System Condition", "Scrape Failed", delta="Halted", delta_color="inverse")
            st.stop()
            
        log_messages.append(f"Successfully scraped and loaded {len(proxy_list)} live public proxies into memory!")
        log_box.code("\n".join(log_messages), language="text")

        # Headless Configuration Stack
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        try:
            driver_path = ChromeDriverManager().install()
        except Exception as e:
            st.error(f"Driver Resolution Failure: {e}")
            metric_status.metric("System Condition", "Fatal Error", delta="Crashed", delta_color="inverse")
            st.stop()

        accumulated_seconds = 0
        successful_deployments = 0

        # Automation Routine Iteration
        for i in range(1, total_runs + 1):
            # Pick a proxy randomly from the freshly generated pool
            current_proxy = random.choice(proxy_list)
            
            # Recreate unique cleaner arguments per execution thread loop
            loop_options = Options()
            for arg in chrome_options.arguments:
                loop_options.add_argument(arg)
            loop_options.add_argument(f"--proxy-server={current_proxy}")
            
            metric_workers.metric("Active Progress", f"{i} / {total_runs}", f"+1 Worker")
            metric_status.metric("System Condition", f"Running Worker {i}", delta="Processing")
            
            msg = f"[{time.strftime('%X')}] 🟢 Launching headless worker {i}/{total_runs} via proxy {current_proxy}"
            log_messages.append(msg)
            log_box.code("\n".join(log_messages), language="text")

            try:
                driver = webdriver.Chrome(service=Service(driver_path), options=loop_options)
                driver.get(url)
                
                lifetime = random.randint(min_duration, max_duration)
                accumulated_seconds += lifetime
                successful_deployments += 1
                
                metric_time.metric("Total Engagement Time", f"{accumulated_seconds}s", f"~{int(accumulated_seconds/successful_deployments)}s avg")
                
                log_messages.append(f"   -> Connected. Retaining viewport session runtime for {lifetime} seconds...")
                log_box.code("\n".join(log_messages), language="text")
                
                time.sleep(lifetime)
                driver.quit()
                log_messages.append(f"   -> [{time.strftime('%X')}] 🔴 Connection terminated safely.")
            except Exception as e:
                log_messages.append(f"   -> ⚠️ Worker connection timed out or failed proxy check: {str(e)[:50]}")
            
            progress_bar.progress(float(i / total_runs))
            log_box.code("\n".join(log_messages), language="text")

            if i < total_runs:
                interval_sleep = random.randint(min_duration, max_duration)
                log_messages.append(f"[{time.strftime('%X')}] Cooling down for {interval_sleep}s before spawning next session instance...\n")
                log_box.code("\n".join(log_messages), language="text")
                time.sleep(interval_sleep)

        st.success("🎉 Automation campaign successfully finished!")
        metric_status.metric("System Condition", "Finished", delta="Idle", delta_color="off")
