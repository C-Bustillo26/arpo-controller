class InverterController:
    def __init__(self):
        self.running = False

    def start(self):
        if not self.running:
            print("[Inverter] Starting inverter...")
            self.running = True

    def stop(self):
        if self.running:
            print("[Inverter] Stopping inverter...")
            self.running = False

    def status(self):
        return "ON" if self.running else "OFF"
