import Logo from "../common/Logo"
import FaceBookIcon from '@/assets/images/icons/facebook-logo.png'
import InstagramIcon from '@/assets/images/icons/instagram-logo.png'
import TwitterIcon from '@/assets/images/icons/twitter-logo.png'
import MailIcon from '@/assets/images/icons/mail-logo.png'

function SocialIconButton({icon}) {
    return (
        <button className="rounded-full border-4 border-white w-14 h-14 justify-center items-center mx-auto flex hover:bg-green-400 transition-all duration-300">
            <img src={icon} alt="" 
            className="w-8 h-8 invert"/>
        </button>
    )
}

function Footer() {
    return (
        <footer className="flex flex-col bg-green-800 py-20 space-y-20">
            {/* First div */}
            
            <div className="h-[50%]  flex flex-row px-20 space-x-[20%]">
                <div className="flex flex-col items-center space-y-6">
                    <Logo size={150} mode='light'></Logo>
                    <h1 className="text-3xl font-semibold text-white">E-LIB PROMAX</h1>
                </div>

                <div className="flex flex-row justify-evenly gap-12" >
                    <div className="text-white text-2xl flex flex-col">
                        <p>Horror</p>
                        <p>Brainrot</p>
                        <p>Romance</p>
                    </div>
                    <div className="text-white text-2xl flex flex-col">
                        <p>Bromance</p>
                        <p>Helo</p>
                        <p>Tralalelo</p>
                    </div>
                    <div className="text-white text-2xl flex flex-col">
                        <p>Bla bla</p>
                        <p>Konichiwa</p>
                        <p>Tung tung tung</p>
                    </div>
                    <div className="text-white text-2xl flex flex-col">
                        <p>Oyasumi</p>
                        <p>HEHEE</p>
                        <p>Gaoooo</p>
                        <p>Chimpanzene</p>
                    </div>
                </div>
            </div>

            <div className="border-2 rounded-xl border-white w-[90%] mx-auto"></div>

            <div className="mx-auto items-center justify-center flex flex-row space-x-6" >
                <SocialIconButton icon={FaceBookIcon}></SocialIconButton>
                <SocialIconButton icon={InstagramIcon}></SocialIconButton>
                <SocialIconButton icon={TwitterIcon}></SocialIconButton>
                <SocialIconButton icon={MailIcon}></SocialIconButton>

            </div>
            <h2 className="text-white mx-auto font-serif text-xl">@Copyright served (maybe)</h2>
        </footer>
    )
}

export default Footer