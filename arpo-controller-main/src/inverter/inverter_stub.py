class InverterController:
    def __init__(self):
        self.running = False
        print("[Inverter] Stub mode active.")

    def start(self):
        if not self.running:
            print("[Inverter] Starting inverter (stub)...")
            self.running = True

    def stop(self):
        if self.running:
            print("[Inverter] Stopping inverter (stub)...")
            self.running = False

    def status(self):
        return "ON" if self.running else "OFF"
