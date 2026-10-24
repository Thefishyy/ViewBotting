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

# MULTI-SOURCE FALLBACK ENGINE: Tries multiple distinct URLs if one fails
def fetch_fresh_proxies():
    sources = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://api.proxyscrape.com/?request=displayproxies&proxytype=http",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://api.openproxylist.xyz/http.txt"
    ]
    
    for url in sources:
        try:
            # Short timeout per source to keep the UI snappy
            response = requests.get(url, timeout=5)
            if response.status_code == 200 and len(response.text.strip()) > 50:
                raw_proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
                if raw_proxies:
                    return raw_proxies
        except Exception:
            continue # Try next url source if current fails
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
        log_messages.append("[Scraping live proxies using redundant endpoint arrays...]")
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
        
        # TIMEOUT GUARD
        chrome_options.page_load_strategy = 'eager'

        try:
            driver_path = ChromeDriverManager().install()
        except Exception as e:
            st.error(f"Driver Resolution Failure: {e}")
            metric_status.metric("System Condition", "Fatal Error", delta="Crashed", delta_color="inverse")
            st.stop()

        accumulated_seconds = 0
        successful_deployments = 0

        # Automation Routine Iteration
        i = 1
        while successful_deployments < total_runs:
            current_proxy = random.choice(proxy_list)
            
            loop_options = Options()
            for arg in chrome_options.arguments:
                loop_options.add_argument(arg)
            loop_options.add_argument(f"--proxy-server={current_proxy}")
            
            metric_workers.metric("Active Progress", f"{successful_deployments} / {total_runs}", f"Worker Run #{i}")
            metric_status.metric("System Condition", f"Trying Worker {successful_deployments + 1}", delta="Processing")
            
            msg = f"[{time.strftime('%X')}] 🟢 Launching worker via proxy {current_proxy}"
            log_messages.append(msg)
            log_box.code("\n".join(log_messages), language="text")

            driver = None
            try:
                driver = webdriver.Chrome(service=Service(driver_path), options=loop_options)
                driver.set_page_load_timeout(12) 
                driver.get(url)
                
                lifetime = random.randint(min_duration, max_duration)
                accumulated_seconds += lifetime
                successful_deployments += 1
                
                metric_time.metric("Total Engagement Time", f"{accumulated_seconds}s", f"~{int(accumulated_seconds/successful_deployments)}s avg")
                
                log_messages.append(f"   -> Connected! Success count: {successful_deployments}/{total_runs}. Keeping session active for {lifetime}s...")
                log_box.code("\n".join(log_messages), language="text")
                
                time.sleep(lifetime)
                log_messages.append(f"   -> [{time.strftime('%X')}] 🔴 Session complete.")
                
            except Exception as e:
                log_messages.append(f"   -> ⚠️ Proxy timed out, dead, or blocked. Skipping instantly...")
            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass
            
            progress_bar.progress(float(successful_deployments / total_runs))
            log_box.code("\n".join(log_messages), language="text")

            if successful_deployments < total_runs:
                interval_sleep = random.randint(2, 5)
                time.sleep(interval_sleep)
            
            i += 1
            
            if i > (total_runs * 10):
                log_messages.append("\n⚠️ Loop halted safely: Too many dead proxies encountered consecutively.")
                log_box.code("\n".join(log_messages), language="text")
                break

        st.success("🎉 Automation campaign successfully finished!")
        metric_status.metric("System Condition", "Finished", delta="Idle", delta_color="off")
