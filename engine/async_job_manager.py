"""AsyncJobManager class for managing asynchronous image mixing jobs."""

import threading
import time
from typing import Dict, Optional, List, Callable, Any
from models.image_model import ImageModel
from .mixer_engine import MixerEngine


class AsyncJobManager:
    """Manages asynchronous image mixing jobs."""

    def __init__(self):
        """Initialize AsyncJobManager."""
        self._mixer_engine = MixerEngine()
        self._current_job: Optional[threading.Thread] = None
        self._job_cancelled = False
        self._progress = 0.0
        self._result: Optional[any] = None
        self._lock = threading.Lock()

    def start_mixing_job(self, inputs: Dict[str, Any], callback: Optional[Callable] = None) -> None:
        """
        Start a new image mixing job.

        Args:
            inputs: Dictionary containing all necessary data for the mixer engine.
                    (mode, weights1, weights2, images, mask, etc.)
            callback: Optional callback function to call when job completes
        """
        # Cancel any existing job
        self.cancel_current_job()

        # Reset state
        with self._lock:
            self._job_cancelled = False
            self._progress = 0.0
            self._result = None

        # Start new job in background thread
        def job_worker():
            try:
                # Simulate initial progress to show responsiveness
                with self._lock:
                    if self._job_cancelled:
                        return
                    self._progress = 0.1

                # Perform mixing
                # CHANGE: Delegated unpacking logic to MixerEngine.run_async_task
                # This keeps the Thread Manager generic and the Logic in the Engine.
                result = self._mixer_engine.run_async_task(inputs)

                with self._lock:
                    if self._job_cancelled:
                        return
                    self._progress = 1.0
                    self._result = result

                # Call callback if provided
                if callback:
                    callback(result)

            except Exception as e:
                # Log error if needed, or handle gracefully
                print(f"Job Error: {e}")
                with self._lock:
                    self._progress = -1.0  # Error state
                    self._result = None
                if callback:
                    callback(None)

        self._current_job = threading.Thread(target=job_worker, daemon=True)
        self._current_job.start()

    def cancel_current_job(self) -> None:
        """Cancel the currently running job."""
        with self._lock:
            self._job_cancelled = True

        if self._current_job and self._current_job.is_alive():
            # Wait a bit for the thread to finish (optional, prevents zombie threads)
            self._current_job.join(timeout=0.1)

    def get_progress(self) -> float:
        """
        Retrieve the progress of the current job.

        Returns:
            Progress value between 0.0 and 1.0, or -1.0 if error
        """
        with self._lock:
            return self._progress

    def get_result(self) -> Optional[any]:
        """
        Get the result of the completed job.

        Returns:
            Result array if job completed successfully, None otherwise
        """
        with self._lock:
            return self._result

    def is_job_running(self) -> bool:
        """
        Check if a job is currently running.

        Returns:
            True if job is running, False otherwise
        """
        if self._current_job is None:
            return False
        return self._current_job.is_alive()