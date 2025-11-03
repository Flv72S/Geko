import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: (user, token) => {
        localStorage.setItem('geko_token', token);
        localStorage.setItem('geko_user', JSON.stringify(user));
        set({
          user,
          token,
          isAuthenticated: true,
        });
      },

      logout: () => {
        localStorage.removeItem('geko_token');
        localStorage.removeItem('geko_user');
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      initialize: () => {
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
        }
      },
    }),
    {
      name: 'geko-auth-storage',
    }
  )
);

export default useAuthStore;

