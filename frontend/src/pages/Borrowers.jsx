import { useEffect, useState } from 'react';
import {
  listBorrowers,
  createBorrower,
  updateBorrower,
  deleteBorrower,
  errorMessage,
} from '../api.js';
import Modal from '../components/Modal.jsx';

const EMPTY_FORM = { borrower_name: '', email: '', phone: '' };
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function Borrowers() {
  const [borrowers, setBorrowers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('');

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formErrors, setFormErrors] = useState({});
  const [saving, setSaving] = useState(false);

  async function reload() {
    try {
      setLoading(true);
      setBorrowers(await listBorrowers());
      setError('');
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { reload(); }, []);

  function openCreate() {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormErrors({});
    setModalOpen(true);
  }

  function openEdit(b) {
    setEditing(b);
    setForm({
      borrower_name: b.borrower_name,
      email: b.email,
      phone: b.phone,
    });
    setFormErrors({});
    setModalOpen(true);
  }

  function validate() {
    const errs = {};
    if (!form.borrower_name.trim()) errs.borrower_name = 'Name is required';
    if (!form.email.trim()) errs.email = 'Email is required';
    else if (!EMAIL_RE.test(form.email.trim())) errs.email = 'Invalid email format';
    if (!form.phone.trim()) errs.phone = 'Phone is required';
    else if (form.phone.trim().length < 5) errs.phone = 'Phone too short';
    setFormErrors(errs);
    return Object.keys(errs).length === 0;
  }

  async function submit(e) {
    e.preventDefault();
    if (!validate()) return;
    try {
      setSaving(true);
      if (editing) {
        await updateBorrower(editing.borrower_id, form);
      } else {
        await createBorrower(form);
      }
      setModalOpen(false);
      await reload();
    } catch (err) {
      setFormErrors({ _form: errorMessage(err) });
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(b) {
    if (!window.confirm(`Delete borrower "${b.borrower_name}"?`)) return;
    try {
      await deleteBorrower(b.borrower_id);
      await reload();
    } catch (e) {
      setError(errorMessage(e));
    }
  }

  const filtered = borrowers.filter((b) => {
    if (!filter) return true;
    const q = filter.toLowerCase();
    return (
      b.borrower_name.toLowerCase().includes(q) ||
      b.email.toLowerCase().includes(q) ||
      b.phone.includes(q)
    );
  });

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Borrowers</h1>
          <div className="page-subtitle">Library members</div>
        </div>
        <button className="btn btn-primary" onClick={openCreate}>+ Add Borrower</button>
      </div>

      {error && <div className="alert">{error}</div>}

      <div className="toolbar">
        <input
          className="input"
          placeholder="Filter by name, email or phone…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
        <span className="page-subtitle">
          {filtered.length} of {borrowers.length}
        </span>
      </div>

      {loading ? (
        <div className="loading">Loading borrowers…</div>
      ) : filtered.length === 0 ? (
        <div className="card empty">
          <div className="empty-title">No borrowers found</div>
          <div>Add a new borrower to get started.</div>
        </div>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((b) => (
                <tr key={b.borrower_id}>
                  <td>{b.borrower_id}</td>
                  <td>{b.borrower_name}</td>
                  <td>{b.email}</td>
                  <td>{b.phone}</td>
                  <td>
                    <div className="btn-row">
                      <button className="btn btn-sm" onClick={() => openEdit(b)}>Edit</button>
                      <button
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDelete(b)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={modalOpen}
        title={editing ? 'Edit borrower' : 'Add new borrower'}
        onClose={() => setModalOpen(false)}
      >
        <form className="form" onSubmit={submit}>
          {formErrors._form && <div className="alert">{formErrors._form}</div>}
          <div className="form-field">
            <label>Full name</label>
            <input
              className={'input' + (formErrors.borrower_name ? ' input-error' : '')}
              value={form.borrower_name}
              onChange={(e) => setForm({ ...form, borrower_name: e.target.value })}
            />
            {formErrors.borrower_name && (
              <div className="field-error">{formErrors.borrower_name}</div>
            )}
          </div>
          <div className="form-row">
            <div className="form-field">
              <label>Email</label>
              <input
                type="email"
                className={'input' + (formErrors.email ? ' input-error' : '')}
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
              {formErrors.email && <div className="field-error">{formErrors.email}</div>}
            </div>
            <div className="form-field">
              <label>Phone</label>
              <input
                className={'input' + (formErrors.phone ? ' input-error' : '')}
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
              />
              {formErrors.phone && <div className="field-error">{formErrors.phone}</div>}
            </div>
          </div>
          <div className="modal-actions">
            <button
              type="button"
              className="btn"
              onClick={() => setModalOpen(false)}
              disabled={saving}
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving…' : editing ? 'Save changes' : 'Add borrower'}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
