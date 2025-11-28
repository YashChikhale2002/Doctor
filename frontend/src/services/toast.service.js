/**
 * Toast notification service using react-toastify
 */

import { toast } from 'react-toastify';

class ToastService {
  success(message, options = {}) {
    toast.success(message, {
      position: 'top-right',
      autoClose: 3000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      ...options,
    });
  }

  error(message, options = {}) {
    toast.error(message, {
      position: 'top-right',
      autoClose: 5000,
      ...options,
    });
  }

  info(message, options = {}) {
    toast.info(message, {
      position: 'top-right',
      autoClose: 3000,
      ...options,
    });
  }

  warning(message, options = {}) {
    toast.warning(message, {
      position: 'top-right',
      autoClose: 4000,
      ...options,
    });
  }

  promise(promise, messages) {
    return toast.promise(
      promise,
      {
        pending: messages.pending || 'Processing...',
        success: messages.success || 'Success!',
        error: messages.error || 'Error occurred',
      },
      {
        position: 'top-right',
      }
    );
  }
}

export const toastService = new ToastService();
