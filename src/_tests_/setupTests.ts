import '@testing-library/jest-dom';
import 'whatwg-fetch';

// Set process.env for Jest
process.env.VITE_API_URL = 'http://localhost:8001/api';

// Polyfill window.matchMedia for jsdom
if (typeof window !== 'undefined' && !window.matchMedia) {
  window.matchMedia = function (query) {
    return {
      matches: false,
      media: query,
      onchange: null,
      addListener: function () {},
      removeListener: function () {},
      addEventListener: function () {},
      removeEventListener: function () {},
      dispatchEvent: function () { return false; },
    };
  };
}
