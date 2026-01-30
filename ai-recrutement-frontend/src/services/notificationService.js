import api from './api';

export const getNotifications = async () => {
  try {
    const { data } = await api.get('/notifications');
    return { data: Array.isArray(data) ? data : [] };
  } catch {
    return { data: [] };
  }
};

export const markAsRead = async (id) => {
  try {
    await api.patch(`/notifications/${id}/read`);
  } catch {
    // backend may not have this route yet
  }
};
