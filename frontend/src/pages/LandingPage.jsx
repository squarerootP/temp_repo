import NavBar from "@/components/layout/Navbar"
import { styles } from "../styles/style_config"
import Footer from "../components/layout/Footer"
function LangdingPage() {
    return (
        <div>
            <NavBar></NavBar>
            <div className={styles.main_bg}>
                <div className="rounded-lg bg-white scale-110">
                    <h1>Landing</h1>
                </div>    
            </div>
            <Footer></Footer>
        </div>
    )
}

export default LangdingPage