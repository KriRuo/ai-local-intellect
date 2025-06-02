/**
 * Simple logger utility that handles different log levels and environments
 */
const logger = {
  debug: (message: string, ...args: any[]) => {
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[DEBUG] ${message}`, ...args);
    }
  },

  info: (message: string, ...args: any[]) => {
    console.info(`[INFO] ${message}`, ...args);
  },

  warn: (message: string, ...args: any[]) => {
    console.warn(`[WARN] ${message}`, ...args);
  },

  error: (message: string, error?: any) => {
    console.error(`[ERROR] ${message}`, error);
  }
};

export { logger }; 