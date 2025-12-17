import api from './api';
import { Customer, CustomerCreate, Deal, DealCreate, Contact, ContactCreate, Activity, ActivityCreate } from '../types';

// Customers
export const getCustomers = async (): Promise<Customer[]> => {
  const response = await api.get('/customers');
  return response.data;
};

export const getCustomer = async (id: number): Promise<Customer> => {
  const response = await api.get(`/customers/${id}`);
  return response.data;
};

export const createCustomer = async (customer: CustomerCreate): Promise<Customer> => {
  const response = await api.post('/customers', customer);
  return response.data;
};

export const updateCustomer = async (id: number, customer: Partial<CustomerCreate>): Promise<Customer> => {
  const response = await api.put(`/customers/${id}`, customer);
  return response.data;
};

export const deleteCustomer = async (id: number): Promise<void> => {
  await api.delete(`/customers/${id}`);
};

// Deals
export const getDeals = async (): Promise<Deal[]> => {
  const response = await api.get('/deals');
  return response.data;
};

export const getDeal = async (id: number): Promise<Deal> => {
  const response = await api.get(`/deals/${id}`);
  return response.data;
};

export const createDeal = async (deal: DealCreate): Promise<Deal> => {
  const response = await api.post('/deals', deal);
  return response.data;
};

export const updateDeal = async (id: number, deal: Partial<DealCreate>): Promise<Deal> => {
  const response = await api.put(`/deals/${id}`, deal);
  return response.data;
};

export const deleteDeal = async (id: number): Promise<void> => {
  await api.delete(`/deals/${id}`);
};

// Contacts
export const getContacts = async (): Promise<Contact[]> => {
  const response = await api.get('/contacts');
  return response.data;
};

export const getContact = async (id: number): Promise<Contact> => {
  const response = await api.get(`/contacts/${id}`);
  return response.data;
};

export const createContact = async (contact: ContactCreate): Promise<Contact> => {
  const response = await api.post('/contacts', contact);
  return response.data;
};

export const updateContact = async (id: number, contact: Partial<ContactCreate>): Promise<Contact> => {
  const response = await api.put(`/contacts/${id}`, contact);
  return response.data;
};

export const deleteContact = async (id: number): Promise<void> => {
  await api.delete(`/contacts/${id}`);
};

// Activities
export const getActivities = async (): Promise<Activity[]> => {
  const response = await api.get('/activities');
  return response.data;
};

export const getActivity = async (id: number): Promise<Activity> => {
  const response = await api.get(`/activities/${id}`);
  return response.data;
};

export const createActivity = async (activity: ActivityCreate): Promise<Activity> => {
  const response = await api.post('/activities', activity);
  return response.data;
};

export const updateActivity = async (id: number, activity: Partial<ActivityCreate>): Promise<Activity> => {
  const response = await api.put(`/activities/${id}`, activity);
  return response.data;
};

export const deleteActivity = async (id: number): Promise<void> => {
  await api.delete(`/activities/${id}`);
};
