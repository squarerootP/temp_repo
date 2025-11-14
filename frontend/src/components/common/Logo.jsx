import appLogo from '@/assets/images/logo/app_logo_3.png';

function Logo({ size = 48, mode = 'light' }) {
  const filterStyle = mode === 'light' ? { filter: 'invert(1)' } : { filter: 'invert(0)' };

  return <img src={appLogo} alt='Logo' width={size} height={size} style={filterStyle} />;
}
export default Logo;
