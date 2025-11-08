import { Link } from "react-router-dom";
import {FormField} from "@components/forms/FormField.jsx";
import { SubmitButton } from "@components/forms/SubmitButton.jsx";
import { use, useState } from "react";
import { useNavigate } from "react-router-dom";
import {styles} from "@styles/style_config.jsx"
import SignUpForm from "@/components_data/forms/SignUpForm.json"
import { useEffect } from "react";
function SignUp(){

    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")
    const [phone, setPhone] = useState("")
    const [address, setAddress] = useState("")

    const [errors, setErrors] = useState({})

    const navigate = useNavigate()

    const validateForm = () => {
        const newErrors = {}

        if (!username.trim()) newErrors.username = "Username is required"
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!email.trim()) newErrors.email = "Email is required"
        else if (!emailRegex.test(email)) newErrors.email = "Invalid email format"

        if (password.length < 6) newErrors.password = "Password must be at least 6 characters"
        if (password !== confirmPassword) newErrors.confirmPassword = "Passwords do not match"

        return {
            isValid: Object.keys(newErrors).length === 0,
            newErrors
        }
    }
    const {isValid} = validateForm()
    const isDisabled = !isValid

    useEffect(() => {
        const {newErrors} = validateForm() 
        setErrors(validateForm().newErrors)
    }, [username, email, password, confirmPassword])

    function handleSubmit(e) {
        e.preventDefault()

        try {
            alert("Sign up successful!")
            navigate('/login')
        } catch (err) {
            
        }
    }
    return (
        <div className={styles.main_bg} >
            <div className={styles.form_bg}>
                <h2  className={styles.main_form_header}>
                    {SignUpForm.header}
                </h2>
                <form onSubmit={handleSubmit} className="space-y-5" >
                    <FormField
                        label="Username"
                        type="text"
                        placeholder="username..."
                        onChange={(e) => setUsername(e.target.value)}
                        error={errors.username}
                        required={true}
                    />

                    <FormField
                        label="Email"
                        type="email"
                        placeholder="you@example.com"
                        onChange={(e) => setEmail(e.target.value)}
                        required={true}
                        error={errors.email}
                    />

                    <FormField
                        label="Password"
                        type="password"
                        placeholder="your password..."
                        onChange={(e) => setPassword(e.target.value)}
                        required={true}
                        error={errors.password}
                    />

                    <FormField
                        label="Confirm password"
                        type="password"
                        placeholder="confirm your password..."
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required={true}
                        error={errors.confirmPassword}
                    />

                    <FormField
                        label="Phone Number"
                        type="phonenumber"
                        placeholder="your phone number..."
                        onChange={(e) => setPhone(e.target.value)}
                        required={false}
                    />

                    <FormField
                        label="Address"
                        type="address"
                        placeholder="your address..."
                        onChange={(e) => setAddress(e.target.value)}
                        required={false}
                    />
                    <SubmitButton text="Sign up" isDisabled={isDisabled}/>

                </form>
                <p className="text-sm text-center mt-4 ">{SignUpForm.route_to_sign_in} {" "}
                <Link to="/login" className="text-green-600 hover:underline">{SignUpForm.sign_in_link_text}</Link>
                </p>
            </div>
        </div>
    )
}
export default SignUp;