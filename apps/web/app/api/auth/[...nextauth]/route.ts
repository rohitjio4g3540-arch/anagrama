import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) return null;
        
        try {
          const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/auth/token`, {
            method: 'POST',
            body: new URLSearchParams({
              username: credentials.username,
              password: credentials.password,
            }),
            headers: { "Content-Type": "application/x-www-form-urlencoded" }
          });
          const user = await res.json();
          if (res.ok && user && user.access_token) {
            return { id: user.user_id, name: credentials.username, accessToken: user.access_token };
          }
        } catch (e) {
          console.error("Auth error:", e);
        }
        return null;
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = (user as any).accessToken;
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      (session as any).accessToken = token.accessToken;
      if (session.user) {
        session.user.name = token.name;
        (session.user as any).id = token.id;
      }
      return session;
    }
  },
  session: { strategy: "jwt" }
});

export { handler as GET, handler as POST };
