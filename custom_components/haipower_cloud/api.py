"""API Client for Aohai Digital Power / HaiPower platform."""
import logging
import base64
import json
import hashlib
import time
import requests

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://eu.aohaidigitalpower.com"

class AohaiApiError(Exception):
    """Exception raised for errors in Aohai API."""
    pass

class AohaiAuthError(AohaiApiError):
    """Exception raised for authentication errors."""
    pass

class AohaiApiClient:
    """Client for communicating with eu.aohaidigitalpower.com."""

    def __init__(self, username, password):
        self.username = username
        # If password is already an MD5 hex string (32 chars hex), keep it, otherwise compute MD5
        if len(password) == 32 and all(c in "0123456789abcdefABCDEF" for c in password):
            self.password_hash = password.lower()
        else:
            self.password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": f"{BASE_URL}/"
        })
        self.user_id = None
        self.token = None
        self.token_expiry = 0

    def login(self):
        """Authenticate with the Aohai platform using automatic captcha resolution."""
        _LOGGER.debug("Attempting login for user %s", self.username)
        try:
            # 1. Request verification image & cookie
            res = self.session.get(f"{BASE_URL}/auth/getCode", timeout=15)
            cookie_check_code = self.session.cookies.get("cookie_check_code")
            if not cookie_check_code:
                raise AohaiAuthError("Failed to obtain verification cookie from server")

            # 2. Extract captcha code from the JWT payload
            parts = cookie_check_code.split(".")
            if len(parts) < 2:
                raise AohaiAuthError("Invalid cookie_check_code format")
            
            payload_b64 = parts[1] + "=="
            payload_str = base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8")
            payload = json.loads(payload_str)
            code_val = payload.get("user_id")

            if not code_val:
                raise AohaiAuthError("Verification code not found in server response")

            # 3. Post login
            login_data = {
                "code": str(code_val),
                "password": self.password_hash,
                "userName": self.username
            }
            login_res = self.session.post(f"{BASE_URL}/auth/doLogin", data=login_data, timeout=15)
            resp_json = login_res.json()

            if resp_json.get("code") != 200:
                raise AohaiAuthError(f"Login rejected: {resp_json.get('msg', 'Unknown error')}")

            user_data = resp_json.get("data", {})
            self.user_id = user_data.get("id")
            self.token = self.session.cookies.get("AUTH_USER_TOKEN")
            self.session.headers["system_hid"] = str(self.user_id)
            
            # Token is valid for 6 hours; schedule refresh after 5 hours
            self.token_expiry = time.time() + (5 * 3600)
            _LOGGER.info("Successfully logged into Aohai HaiPower (User ID: %s)", self.user_id)
            return True
        except requests.RequestException as err:
            raise AohaiApiError(f"Network error during login: {err}") from err

    def _ensure_authenticated(self):
        """Ensure active login session, re-authenticating if needed."""
        if not self.token or time.time() >= self.token_expiry:
            self.login()

    def get_devices(self):
        """Fetch list of associated devices."""
        self._ensure_authenticated()
        try:
            url = f"{BASE_URL}/view/device/list?id=0&offset=0&pageNum=1&pageSize=20&type=0"
            res = self.session.get(url, timeout=15)
            data = res.json()
            if data.get("code") in (401, 501):
                # Token expired, re-login once
                self.login()
                res = self.session.get(url, timeout=15)
                data = res.json()
            
            rows = data.get("data", {}).get("rows", [])
            return rows
        except requests.RequestException as err:
            raise AohaiApiError(f"Failed to fetch devices: {err}") from err

    def get_device_info(self, dsn):
        """Fetch real-time telemetry and state for a device (/view/data/deviceInfo)."""
        self._ensure_authenticated()
        try:
            url = f"{BASE_URL}/view/data/deviceInfo?dsn={dsn}"
            res = self.session.get(url, timeout=15)
            data = res.json()
            if data.get("code") in (401, 501):
                self.login()
                res = self.session.get(url, timeout=15)
                data = res.json()
            
            return data.get("data", {})
        except requests.RequestException as err:
            raise AohaiApiError(f"Failed to fetch device info for {dsn}: {err}") from err

    def get_detailed_info(self, dsn):
        """Fetch detailed hardware and battery information (/view/device/info?sn=...)."""
        self._ensure_authenticated()
        try:
            url = f"{BASE_URL}/view/device/info?sn={dsn}"
            res = self.session.get(url, timeout=15)
            data = res.json()
            if data.get("code") in (401, 501):
                self.login()
                res = self.session.get(url, timeout=15)
                data = res.json()

            if data.get("code") == 200 and isinstance(data.get("data"), dict):
                return data["data"]
            return {}
        except requests.RequestException as err:
            _LOGGER.error("Failed to fetch detailed info for %s: %s", dsn, err)
            return {}

    def get_params_info(self, dsn):
        """Fetch settings and configuration parameters for a device."""
        self._ensure_authenticated()
        try:
            url = f"{BASE_URL}/view/device/paramsInfo?dsn={dsn}"
            res = self.session.get(url, timeout=15)
            data = res.json()
            if data.get("code") in (401, 501):
                self.login()
                res = self.session.get(url, timeout=15)
                data = res.json()
            
            return data.get("data", {})
        except requests.RequestException as err:
            raise AohaiApiError(f"Failed to fetch params info for {dsn}: {err}") from err

    def set_parameter(self, csn, dsn, addr, key_value_list):
        """Send setting commands to the inverter.
        
        Example: key_value_list = ['onOff=1'] or ['periodpower=2']
        """
        self._ensure_authenticated()
        try:
            payload = {
                "csn": csn,
                "dsn": dsn,
                "addr": addr,
                "keyValue": key_value_list
            }
            url = f"{BASE_URL}/view/hard/set"
            res = self.session.post(url, json=payload, timeout=15)
            data = res.json()
            if data.get("code") in (401, 501):
                self.login()
                res = self.session.post(url, json=payload, timeout=15)
                data = res.json()

            if data.get("code") != 200:
                raise AohaiApiError(f"Command failed: {data.get('msg', 'Unknown error')}")
            
            _LOGGER.info("Parameter set successful for %s: %s", dsn, key_value_list)
            return True
        except requests.RequestException as err:
            raise AohaiApiError(f"Failed to set parameter for {dsn}: {err}") from err

    def set_one_register(self, csn, addr, register, value):
        """Set a single register on the inverter using form-urlencoded data.
        
        Used for special hardware calibration commands like CT Calibration (reg 96, val 1)
        and CT Detection (reg 96, val 2).
        """
        self._ensure_authenticated()
        try:
            payload = {
                "csn": str(csn),
                "addr": int(addr),
                "register": int(register),
                "value": int(value),
            }
            url = f"{BASE_URL}/view/hard/setOneRegister"
            res = self.session.post(url, data=payload, timeout=15)
            data = res.json()
            if data.get("code") in (401, 501):
                self.login()
                res = self.session.post(url, data=payload, timeout=15)
                data = res.json()

            if data.get("code") != 200:
                raise AohaiApiError(f"Register command failed: {data.get('msg', 'Unknown error')}")

            _LOGGER.info("Set register %s=%s successful for CSN %s", register, value, csn)
            return True
        except requests.RequestException as err:
            raise AohaiApiError(f"Failed to set register {register} for {csn}: {err}") from err
