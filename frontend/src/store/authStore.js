import { create } from 'zustand';

// Helper per accedere a localStorage in modo sicuro (solo in browser)
const getStoredAuth = () => {
  if (typeof window === 'undefined') {
    return { user: null, token: null, isAuthenticated: false };
  }
  
  try {
    const token = localStorage.getItem('geko_token');
    const userStr = localStorage.getItem('geko_user');
    
    if (token && userStr) {
      const user = JSON.parse(userStr);
      return { user, token, isAuthenticated: true };
    }
  } catch (error) {
    // Se il parsing fallisce, pulisci tutto
    if (typeof window !== 'undefined') {
      localStorage.removeItem('geko_token');
      localStorage.removeItem('geko_user');
    }
  }
  
  return { user: null, token: null, isAuthenticated: false };
};

const useAuthStore = create((set) => {
  const initialAuth = getStoredAuth();

  return {
    user: initialAuth.user,
    token: initialAuth.token,
    isAuthenticated: initialAuth.isAuthenticated,

    login: (user, token) => {
      if (typeof window !== 'undefined') {
        localStorage.setItem('geko_token', token);
        localStorage.setItem('geko_user', JSON.stringify(user));
      }
      set({
        user,
        token,
        isAuthenticated: true,
      });
    },

    logout: () => {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('geko_token');
        localStorage.removeItem('geko_user');
      }
      set({
        user: null,
        token: null,
        isAuthenticated: false,
      });
    },

    initialize: () => {
      if (typeof window === 'undefined') {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
        return;
      }

      const token = localStorage.getItem('geko_token');
      const userStr = localStorage.getItem('geko_user');
      if (token && userStr) {
        try {
          const user = JSON.parse(userStr);
          set({
            user,
            token,
            isAuthenticated: true,
          });
        } catch (error) {
          // Se il parsing fallisce, pulisci tutto
          localStorage.removeItem('geko_token');
          localStorage.removeItem('geko_user');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          });
        }
      } else {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      }
    },
  };
});

export default useAuthStore;

