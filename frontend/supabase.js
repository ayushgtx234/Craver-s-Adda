const SUPABASE_URL = 'https://svohhctfdzxyuwoezvnv.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_jV__vdBx7dpJyRlTdcWaNA_gy6znInX';

const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Mock session wrapper for Demo bypass
const originalGetSession = supabaseClient.auth.getSession.bind(supabaseClient.auth);
supabaseClient.auth.getSession = async () => {
    const demoSession = localStorage.getItem('demo_session');
    if (demoSession) {
        return { data: { session: JSON.parse(demoSession) }, error: null };
    }
    return await originalGetSession();
};

const originalSignOut = supabaseClient.auth.signOut.bind(supabaseClient.auth);
supabaseClient.auth.signOut = async () => {
    localStorage.removeItem('demo_session');
    return await originalSignOut();
};
