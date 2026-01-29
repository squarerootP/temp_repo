import NavBar from './Navbar';
import Footer from './Footer'; // make sure this is imported

export default function MainLayout({ children }) {


  return (
    <div className="flex min-h-screen">


      {/* Main content area */}
      <div className="flex-1 flex flex-col">
        <header>
          <NavBar />
        </header>

        <main className="flex-1">{children}</main>

        <Footer />
      </div>
    </div>
  );
}
