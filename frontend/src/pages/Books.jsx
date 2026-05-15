import { useEffect, useState } from 'react';
import {
  listBooks,
  createBook,
  updateBook,
  deleteBook,
  errorMessage,
} from '../api.js';
import Modal from '../components/Modal.jsx';

const EMPTY_FORM = { title: '', author: '', category: '', isbn: '' };

export default function Books() {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('');

  // edit/create modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formErrors, setFormErrors] = useState({});
  const [saving, setSaving] = useState(false);

  async function reload() {
    try {
      setLoading(true);
      setBooks(await listBooks());
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

  function openEdit(book) {
    setEditing(book);
    setForm({
      title: book.title,
      author: book.author,
      category: book.category,
      isbn: book.isbn,
    });
    setFormErrors({});
    setModalOpen(true);
  }

  function validate() {
    const errs = {};
    if (!form.title.trim()) errs.title = 'Title is required';
    if (!form.author.trim()) errs.author = 'Author is required';
    if (!form.category.trim()) errs.category = 'Category is required';
    if (!form.isbn.trim()) errs.isbn = 'ISBN is required';
    else if (form.isbn.trim().length < 5) errs.isbn = 'ISBN must be at least 5 chars';
    setFormErrors(errs);
    return Object.keys(errs).length === 0;
  }

  async function submit(e) {
    e.preventDefault();
    if (!validate()) return;
    try {
      setSaving(true);
      if (editing) {
        await updateBook(editing.book_id, form);
      } else {
        await createBook(form);
      }
      setModalOpen(false);
      await reload();
    } catch (err) {
      setFormErrors({ _form: errorMessage(err) });
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(book) {
    if (!window.confirm(`Delete "${book.title}"?`)) return;
    try {
      await deleteBook(book.book_id);
      await reload();
    } catch (e) {
      setError(errorMessage(e));
    }
  }

  const filtered = books.filter((b) => {
    if (!filter) return true;
    const q = filter.toLowerCase();
    return (
      b.title.toLowerCase().includes(q) ||
      b.author.toLowerCase().includes(q) ||
      b.category.toLowerCase().includes(q) ||
      b.isbn.toLowerCase().includes(q)
    );
  });

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Books</h1>
          <div className="page-subtitle">Manage the library catalog</div>
        </div>
        <button className="btn btn-primary" onClick={openCreate}>+ Add Book</button>
      </div>

      {error && <div className="alert">{error}</div>}

      <div className="toolbar">
        <input
          className="input"
          placeholder="Filter by title, author, category or ISBN…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        />
        <span className="page-subtitle">
          {filtered.length} of {books.length}
        </span>
      </div>

      {loading ? (
        <div className="loading">Loading books…</div>
      ) : filtered.length === 0 ? (
        <div className="card empty">
          <div className="empty-title">No books match</div>
          <div>Try a different filter or add a new book.</div>
        </div>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Author</th>
                <th>Category</th>
                <th>ISBN</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((b) => (
                <tr key={b.book_id}>
                  <td>{b.book_id}</td>
                  <td>{b.title}</td>
                  <td>{b.author}</td>
                  <td>{b.category}</td>
                  <td>{b.isbn}</td>
                  <td>
                    <span
                      className={
                        'pill ' +
                        (b.availability_status === 'Available'
                          ? 'pill-available'
                          : 'pill-borrowed')
                      }
                    >
                      {b.availability_status}
                    </span>
                  </td>
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
        title={editing ? 'Edit book' : 'Add new book'}
        onClose={() => setModalOpen(false)}
      >
        <form className="form" onSubmit={submit}>
          {formErrors._form && <div className="alert">{formErrors._form}</div>}
          <div className="form-field">
            <label>Title</label>
            <input
              className={'input' + (formErrors.title ? ' input-error' : '')}
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
            {formErrors.title && <div className="field-error">{formErrors.title}</div>}
          </div>
          <div className="form-row">
            <div className="form-field">
              <label>Author</label>
              <input
                className={'input' + (formErrors.author ? ' input-error' : '')}
                value={form.author}
                onChange={(e) => setForm({ ...form, author: e.target.value })}
              />
              {formErrors.author && <div className="field-error">{formErrors.author}</div>}
            </div>
            <div className="form-field">
              <label>Category</label>
              <input
                className={'input' + (formErrors.category ? ' input-error' : '')}
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
              />
              {formErrors.category && <div className="field-error">{formErrors.category}</div>}
            </div>
          </div>
          <div className="form-field">
            <label>ISBN</label>
            <input
              className={'input' + (formErrors.isbn ? ' input-error' : '')}
              value={form.isbn}
              onChange={(e) => setForm({ ...form, isbn: e.target.value })}
            />
            {formErrors.isbn && <div className="field-error">{formErrors.isbn}</div>}
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
              {saving ? 'Saving…' : editing ? 'Save changes' : 'Add book'}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
