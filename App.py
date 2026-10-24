import streamlit as st
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Page configurations and UI Theme setup
st.set_page_config(
    page_title="Proxy Traffic Deployer", 
    page_icon="🌐",
    layout="wide"
)

# Custom CSS for better structural appearance
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 1200px; }
    div.stButton > button:first-child { width: 100%; margin-top: 15px; }
    .stProgress .st-bo { background-color: #4CAF50; }
    </style>
""", unsafe_allow_html=True)

# Application Header Banner
st.title("🌐 Multi-Proxy Traffic Control Dashboard")
st.markdown("Deploy and monitor automated, proxy-routed browser operations via cloud containers.")
st.divider()

# Sidebar Layout for Configuration Inputs
with st.sidebar:
    st.header("⚙️ Configuration Settings")
    url = st.text_input("Target Destination URL", placeholder="example.com").strip()
    
    st.subheader("⏱️ Worker Lifespans")
    min_duration = st.number_input("Minimum Duration (sec)", min_value=1, value=5)
    max_duration = st.number_input("Maximum Duration (sec)", min_value=1, value=15)
    
    st.subheader("🤖 Fleet Parameters")
    total_runs = st.slider("Total Workers to Deploy", min_value=1, max_value=20, value=6)
    
    launch_btn = st.button("🚀 Launch Campaign", type="primary")

# Proxy Configuration Pool
proxy_list = [
    "40.85.126.23:80", "21.4.196.186:80", "128.252.56.167:80", "233.162.5.50:80",
    "116.176.115.154:80", "244.157.172.120:80", "41.247.81.252:80", "146.165.211.36:80",
    "73.95.186.247:80", "90.117.38.252:80", "247.89.95.173:80", "100.14.70.190:80",
    "170.75.176.22:80", "126.88.14.29:80", "85.4.220.181:80", "81.253.99.206:80",
    "22.10.8.85:80", "216.202.169.242:80", "11.226.166.163:80", "16.190.99.91:80",
    "202.153.142.215:80", "65.113.130.225:80", "215.248.19.238:80", "214.233.114.107:80",
    "72.12.62.41:80", "118.10.233.66:80", "111.211.165.52:80", "119.41.183.254:80",
]

# Dashboard Main Body (Visible analytics elements)
col_m1, col_m2, col_m3 = st.columns(3)
metric_workers = col_m1.metric("Active Progress", "0 / 0", "Pending")
metric_time = col_m2.metric("Total Engagement Time", "0s", "0s avg")
metric_status = col_m3.metric("System Condition", "Idle", delta=None)

progress_bar = st.progress(0.0)
st.subheader("📜 Real-Time Process Monitor Logs")
log_box = st.code("System ready. Configure constraints in the sidebar and trigger deployment.", language="text")

# Application Logic Execution Block
if launch_btn:
    if not url:
        st.error("❌ Action Blocked: A valid destination domain or URL input is required.")
    else:
        # Sanitize URLs
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
            
        if min_duration > max_duration:
            min_duration, max_duration = max_duration, min_duration

        log_messages = ["[System initialization started...]"]
        log_box.code("\n".join(log_messages), language="text")
        metric_status.metric("System Condition", "Initializing...", delta="Active")

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
            current_proxy = proxy_list[(i - 1) % len(proxy_list)]
            chrome_options.add_argument(f"--proxy-server={current_proxy}")
            
            # Live Metrics Update
            metric_workers.metric("Active Progress", f"{i} / {total_runs}", f"+1 Worker")
            metric_status.metric("System Condition", f"Deploying Worker {i}", delta="Processing")
            
            msg = f"[{time.strftime('%X')}] 🟢 Initializing container {i}/{total_runs} via proxy {current_proxy}"
            log_messages.append(msg)
            log_box.code("\n".join(log_messages), language="text")

            try:
                driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
                driver.get(url)
                
                lifetime = random.randint(min_duration, max_duration)
                accumulated_seconds += lifetime
                successful_deployments += 1
                
                # Dynamic update of engagement time metrics
                metric_time.metric("Total Engagement Time", f"{accumulated_seconds}s", f"~{int(accumulated_seconds/successful_deployments)}s avg")
                
                log_messages.append(f"   -> Connected successfully. Retaining browser runtime session for {lifetime} seconds...")
                log_box.code("\n".join(log_messages), language="text")
                
                time.sleep(lifetime)
                driver.quit()
                log_messages.append(f"   -> [{time.strftime('%X')}] 🔴 Connection terminated safely. Worker memory recycled.")
            except Exception as e:
                log_messages.append(f"   -> ⚠️ Worker exception experienced: {str(e)[:60]}")
            
            # Progress bar advancement calculation
            progress_bar.progress(float(i / total_runs))
            log_box.code("\n".join(log_messages), language="text")

            # Interval delay between spawning next headless session
            if i < total_runs:
                interval_sleep = random.randint(min_duration, max_duration)
                log_messages.append(f"[{time.strftime('%X')}] System sleeping for {interval_sleep}s cooldown before spawning next process instance...\n")
                log_box.code("\n".join(log_messages), language="text")
                time.sleep(interval_sleep)

        # Campaign wrap-up state updates
        st.success("🎉 Automation campaign successfully finished!")
        metric_status.metric("System Condition", "Finished", delta="Idle", delta_color="off")
