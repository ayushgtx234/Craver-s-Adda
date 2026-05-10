document.addEventListener('DOMContentLoaded', () => {
    // Phone Number Formatting (+91 and 10 digits max)
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('focus', () => {
            if (!input.value) {
                input.value = '+91 ';
            }
        });

        input.addEventListener('input', (e) => {
            let val = input.value;
            if (!val.startsWith('+91 ')) {
                input.value = '+91 ' + val.replace(/^\+91\s*/, '');
                return;
            }
            let numericPart = val.substring(4).replace(/\D/g, '');
            if (numericPart.length > 10) {
                numericPart = numericPart.substring(0, 10);
            }
            input.value = '+91 ' + numericPart;

            // Auto-trigger OTP sending when 10 digits are reached for real Supabase auth
            if (numericPart.length === 10 && numericPart !== '0000000000') {
                sendOtpSilent(input.value.replace(/\s/g, ''));
            }
        });

        input.addEventListener('click', () => {
            if (input.selectionStart < 4) {
                input.setSelectionRange(4, 4);
            }
        });
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && input.selectionStart <= 4 && input.selectionEnd <= 4) {
                e.preventDefault();
            }
        });
    });

    async function sendOtpSilent(phone) {
        try {
            await supabaseClient.auth.signInWithOtp({ phone });
            console.log('OTP sent to ' + phone);
        } catch (error) {
            console.error('Silent OTP send failed:', error.message);
        }
    }

    // Login Logic
    const loginBtn = document.getElementById('login-btn');
    loginBtn?.addEventListener('click', async () => {
        const phoneInput = document.getElementById('phone-number');
        const otpInputs = document.querySelectorAll('.otp-input');
        const otp = Array.from(otpInputs).map(inp => inp.value).join('');
        const fullPhone = phoneInput.value.replace(/\s/g, '');
        const numericValue = fullPhone.substring(3);

        if (numericValue.length !== 10) {
            alert('Please enter a valid 10-digit phone number');
            return;
        }

        if (otp.length !== 6) {
            alert('Please enter the 6-digit OTP');
            return;
        }

        loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';
        loginBtn.disabled = true;

        // DEMO BYPASS
        if (numericValue === '0000000000' && otp === '123456') {
            const demoSession = {
                user: { id: 'demo-user', phone: '+910000000000' },
                access_token: 'demo-token'
            };
            localStorage.setItem('demo_session', JSON.stringify(demoSession));
            
            const redirect = sessionStorage.getItem('redirect_after_login') || 'index.html';
            sessionStorage.removeItem('redirect_after_login');
            setTimeout(() => { window.location.href = redirect; }, 1000);
            return;
        }

        try {
            const { error } = await supabaseClient.auth.verifyOtp({
                phone: fullPhone,
                token: otp,
                type: 'sms',
            });

            if (error) throw error;
            const redirect = sessionStorage.getItem('redirect_after_login') || 'index.html';
            sessionStorage.removeItem('redirect_after_login');
            window.location.href = redirect;
        } catch (error) {
            alert('Login failed: ' + error.message);
            loginBtn.innerHTML = 'Login';
            loginBtn.disabled = false;
        }
    });

    // Signup Logic
    const signupBtn = document.getElementById('signup-submit-btn');
    signupBtn?.addEventListener('click', async () => {
        const nameInput = document.getElementById('full-name');
        const phoneInput = document.getElementById('phone-number');
        const otpInputs = document.querySelectorAll('.otp-input');
        const otp = Array.from(otpInputs).map(inp => inp.value).join('');
        const name = nameInput.value.trim();
        const fullPhone = phoneInput.value.replace(/\s/g, '');
        const numericValue = fullPhone.substring(3);

        if (!name || numericValue.length !== 10 || otp.length !== 6) {
            alert('Please fill in all fields (Name, Phone, and 6-digit OTP)');
            return;
        }

        signupBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...';
        signupBtn.disabled = true;

        // DEMO BYPASS
        if (numericValue === '0000000000' && otp === '123456') {
            const demoSession = {
                user: { id: 'demo-user', phone: '+910000000000' },
                access_token: 'demo-token'
            };
            localStorage.setItem('demo_session', JSON.stringify(demoSession));
            
            const redirect = sessionStorage.getItem('redirect_after_login') || 'index.html';
            sessionStorage.removeItem('redirect_after_login');
            setTimeout(() => { window.location.href = redirect; }, 1000);
            return;
        }

        try {
            const { data, error } = await supabaseClient.auth.verifyOtp({
                phone: fullPhone,
                token: otp,
                type: 'sms',
            });

            if (error) throw error;

            if (data.user) {
                await supabaseClient.from('profiles').insert({
                    id: data.user.id,
                    full_name: name,
                    phone_number: fullPhone
                });
            }

            const redirect = sessionStorage.getItem('redirect_after_login') || 'index.html';
            sessionStorage.removeItem('redirect_after_login');
            window.location.href = redirect;
        } catch (error) {
            alert('Signup failed: ' + error.message);
            signupBtn.innerHTML = 'Create Account';
            signupBtn.disabled = false;
        }
    });

    // OTP Input Focus Logic (Shared)
    const otpInputs = document.querySelectorAll('.otp-input');
    otpInputs.forEach((input, index) => {
        input.addEventListener('keyup', (e) => {
            if (e.key >= 0 && e.key <= 9) {
                const inputs = input.parentElement.querySelectorAll('.otp-input');
                if (inputs[index + 1]) inputs[index + 1].focus();
            } else if (e.key === 'Backspace') {
                const inputs = input.parentElement.querySelectorAll('.otp-input');
                if (inputs[index - 1]) inputs[index - 1].focus();
            }
        });

        input.addEventListener('paste', (e) => {
            const data = e.clipboardData.getData('text').trim();
            const inputs = input.parentElement.querySelectorAll('.otp-input');
            if (data.length === inputs.length) {
                inputs.forEach((inp, i) => inp.value = data[i]);
                inputs[inputs.length - 1].focus();
            }
        });
    });

    // Auto-fill Demo Credentials
    const demoCredsBtn = document.getElementById('use-demo-creds');
    demoCredsBtn?.addEventListener('click', (e) => {
        e.preventDefault();
        const phoneInput = document.getElementById('phone-number');
        if (phoneInput) {
            phoneInput.value = '+91 0000000000';
        }
        const nameInput = document.getElementById('full-name');
        if (nameInput) {
            nameInput.value = 'Demo User';
        }
        const otpInputs = document.querySelectorAll('.otp-input');
        const demoOtp = '123456';
        otpInputs.forEach((inp, i) => {
            inp.value = demoOtp[i];
        });
    });
});
