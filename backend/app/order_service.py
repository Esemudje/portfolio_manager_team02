import time
import threading
from .order_manager import OrderManager

class OrderExecutionService:
    """Background service to monitor and execute pending orders"""
    
    def __init__(self, check_interval=30):  # Check every 30 seconds
        self.check_interval = check_interval
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the background order execution service"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_service, daemon=True)
            self.thread.start()
            print("Order execution service started")
    
    def stop(self):
        """Stop the background order execution service"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Order execution service stopped")
    
    def _run_service(self):
        """Main service loop"""
        while self.running:
            try:
                print("Checking pending orders for execution...")
                OrderManager.check_and_execute_pending_orders()
            except Exception as e:
                print(f"Error in order execution service: {e}")
            
            # Wait for the next check interval
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)

# Global service instance
order_service = OrderExecutionService()

def start_order_service():
    """Start the order execution service"""
    order_service.start()

def stop_order_service():
    """Stop the order execution service"""
    order_service.stop()
