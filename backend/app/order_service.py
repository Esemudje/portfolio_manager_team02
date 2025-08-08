import time
import threading

class OrderExecutionService:
    """Background service (disabled since we only support market orders that execute immediately)"""
    
    def __init__(self, check_interval=30):
        self.check_interval = check_interval
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the background order execution service (no-op since market orders execute immediately)"""
        print("Order execution service started (no-op for market orders)")
    
    def stop(self):
        """Stop the background order execution service"""
        self.running = False
        print("Order execution service stopped")
    
    def _run_service(self):
        """Main service loop (disabled)"""
        pass

# Global service instance
order_service = OrderExecutionService()

def start_order_service():
    """Start the order execution service"""
    order_service.start()

def stop_order_service():
    """Stop the order execution service"""
    order_service.stop()
