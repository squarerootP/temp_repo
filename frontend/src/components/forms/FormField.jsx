import { styles } from '@/styles/style_config.jsx';

export function FormField({
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  required = false,
}) {
  return (
    <div>
      <label className='block text-sm font-medium text-gray-700 mb-1'>
        {label}
        {required && <span className='text-red-500 ml-1'>*</span>}
      </label>
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={styles.form_field}
        required={required}
      />
      {error && <p className={styles.error_msg}>{error}</p>}
    </div>
  );
}
