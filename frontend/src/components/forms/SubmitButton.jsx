import { styles } from "@styles/style_config"

export function SubmitButton({text, isDisabled = false}){
    return (
        <button type="submit" className={isDisabled ? styles.disabled_btn : styles.submit_btn} disabled={isDisabled}>
            {text}
        </button>
    )
}