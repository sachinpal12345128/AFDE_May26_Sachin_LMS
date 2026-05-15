import { useEffect, useState } from 'react';
import {
  listBooks,
  listBorrowers,
  borrowBook,
  returnBook,
  listTransactions,
  errorMessage,
} from '../api.js';
import Modal from '../components/Modal.jsx';

export default function Transactions() {
  const [books, setBooks] = useState([]);
  const [borrowers, setBorrowers] = useState([]);
  const [txns, setTxns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const [borrowOpen, setBorrowOpen] = useState(false);
  const [form, setForm] = useState({ book_id: '', borrower_id: '' });
  const [formErr, setFormErr] = useState({});
  const [saving, setSaving] = useState(false);

  async function reload() {
    try {
      setLoading(true);
      const [b, br, t] = await Promise.all([
        listBooks(),
        listBorrowers(),
        listTransactions(),
      ]);
      setBooks(b);
      setBorrowers(br);
      setTxns(t);
      setError('');
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { reload(); }, []);

  const availableBooks = books.filter((b) => b.availability_status === 'Available');

  function openBorrow() {
    setForm({ book_id: '', borrower_id: '' });
    setFormErr({});
    setBorrowOpen(true);
  }

  async function submitBorrow(e) {
    e.preventDefault();
    const errs = {};
    if (!form.book_id) errs.book_id = 'Pick a book';
    if (!form.borrower_id) errs.borrower_id = 'Pick a borrower';
    if (Object.keys(errs).length) {
      setFormErr(errs);
      return;
    }
    try {
      setSaving(true);
      await borrowBook({
        book_id: Number(form.book_id),
        borrower_id: Number(form.borrower_id),
      });
      setBorrowOpen(false);
      await reload();
    } catch (err) {
      setFormErr({ _form: errorMessage(err) });
    } finally {
      setSaving(false);
    }
  }

  async function handleReturn(t) {
    if (!window.confirm(`Return "${t.book_title}"?`)) return;
    try {
      await returnBook({ transaction_id: t.transaction_id });
      await reload();
    } catch (e) {
      setError(errorMessage(e));
    }
  }

  const filtered = txns.filter((t) => {
    if (statusFilter === 'open') return !t.return_date;
    if (statusFilter === 'returned') return !!t.return_date;
    return true;
  });

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Transactions</h1>
          <div className="page-subtitle">Borrow and return books</div>
        </div>
        <button
          className="btn btn-primary"
          onClick={openBorrow}
          disabled={availableBooks.length === 0 || borrowers.length === 0}
        >
          + New Borrow
        </button>
      </div>

      {error && <div className="alert">{error}</div>}
      {availableBooks.length === 0 && !loading && (
        <div className="alert alert-info">
          No books are currently available — add new books or wait for returns.
        </div>
      )}

      <div className="toolbar">
        <label className="page-subtitle">Show:</label>
        <select
          className="input"
          style={{ maxWidth: 180 }}
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="all">All</option>
          <option value="open">Open (not returned)</option>
          <option value="returned">Returned</option>
        </select>
        <span className="page-subtitle">
          {filtered.length} of {txns.length}
        </span>
      </div>

      {loading ? (
        <div className="loading">Loading transactions…</div>
      ) : filtered.length === 0 ? (
        <div className="card empty">
          <div className="empty-title">No transactions to show</div>
          <div>Start a new borrow to see it here.</div>
        </div>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Book</th>
                <th>Borrower</th>
                <th>Borrowed at</th>
                <th>Returned at</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((t) => (
                <tr key={t.transaction_id}>
                  <td>{t.transaction_id}</td>
                  <td>{t.book_title}</td>
                  <td>{t.borrower_name}</td>
                  <td>{new Date(t.borrow_date).toLocaleString()}</td>
                  <td>
                    {t.return_date ? new Date(t.return_date).toLocaleString() : '—'}
                  </td>
                  <td>
                    {t.return_date ? (
                      <span className="pill pill-returned">Returned</span>
                    ) : (
                      <span className="pill pill-borrowed">Open</span>
                    )}
                  </td>
                  <td>
                    {!t.return_date && (
                      <button
                        className="btn btn-sm btn-success"
                        onClick={() => handleReturn(t)}
                      >
                        Return
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        open={borrowOpen}
        title="Borrow a book"
        onClose={() => setBorrowOpen(false)}
      >
        <form className="form" onSubmit={submitBorrow}>
          {formErr._form && <div className="alert">{formErr._form}</div>}
          <div className="form-field">
            <label>Book</label>
            <select
              className={'input' + (formErr.book_id ? ' input-error' : '')}
              value={form.book_id}
              onChange={(e) => setForm({ ...form, book_id: e.target.value })}
            >
              <option value="">Select a book…</option>
              {availableBooks.map((b) => (
                <option key={b.book_id} value={b.book_id}>
                  {b.title} — {b.author}
                </option>
              ))}
            </select>
            {formErr.book_id && <div className="field-error">{formErr.book_id}</div>}
          </div>
          <div className="form-field">
            <label>Borrower</label>
            <select
              className={'input' + (formErr.borrower_id ? ' input-error' : '')}
              value={form.borrower_id}
              onChange={(e) => setForm({ ...form, borrower_id: e.target.value })}
            >
              <option value="">Select a borrower…</option>
              {borrowers.map((b) => (
                <option key={b.borrower_id} value={b.borrower_id}>
                  {b.borrower_name} — {b.email}
                </option>
              ))}
            </select>
            {formErr.borrower_id && (
              <div className="field-error">{formErr.borrower_id}</div>
            )}
          </div>
          <div className="modal-actions">
            <button
              type="button"
              className="btn"
              onClick={() => setBorrowOpen(false)}
              disabled={saving}
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Recording…' : 'Borrow'}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
