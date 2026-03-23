# OAuth – Authorisierung

---

## 1. Was ist OAuth?

OAuth (Open Authorization) ist ein offenes Standardprotokoll zur delegierten Autorisierung. Es ermöglicht Anwendungen, eingeschränkten Zugriff auf Benutzerressourcen zu erhalten, ohne dass der Benutzer seine Zugangsdaten an die Anwendung weitergeben muss. Stattdessen erhält die Anwendung einen Token mit definierten Rechten und begrenzter Gültigkeit.

### Authentifizierung vs. Autorisierung

| Konzept             | Fragestellung              | Beispiel                          |
|----------------------|----------------------------|-----------------------------------|
| **Authentifizierung** | Wer ist der Benutzer?     | Login mit Benutzername & Passwort |
| **Autorisierung**     | Was darf der Benutzer?    | Lesezugriff auf Kalender, kein Zugriff auf E-Mails |

OAuth ist ein Autorisierungsprotokoll. Authentifizierung wird über **OpenID Connect (OIDC)** als Schicht auf OAuth 2.0 abgebildet.

---

## 2. Die vier Rollen in OAuth 2.0

### Resource Owner

Die Entität (in der Regel der Endbenutzer), der die geschützten Ressourcen gehören. Erteilt oder verweigert den Zugriff.

### Client

Die Anwendung, die auf geschützte Ressourcen zugreifen will. Wird beim Authorization Server registriert und erhält eine `client_id` sowie ggf. ein `client_secret`.

### Authorization Server

Authentifiziert den Resource Owner, nimmt dessen Zustimmung entgegen und stellt Tokens aus.

### Resource Server

Hostet die geschützten Ressourcen. Akzeptiert Zugriffe ausschließlich mit gültigem Access Token.

### Zusammenspiel

```
┌──────────────┐                        ┌─────────────────────┐
│   Resource    │── (1) Autorisierung ──▶│   Authorization     │
│   Owner       │◀── (2) Zustimmung ────│   Server            │
└──────────────┘                        └─────────┬───────────┘
                                                  │
                                           (3) Access Token
                                                  │
┌──────────────┐                        ┌─────────▼───────────┐
│   Client      │── (4) API-Request ───▶│   Resource          │
│   (App)       │◀── (5) Daten ────────│   Server            │
└──────────────┘                        └─────────────────────┘
```

---

## 3. Token-Typen

### Access Token

- Kurzlebig (Minuten bis Stunden)
- Wird bei jedem API-Aufruf als `Authorization: Bearer <token>` mitgesendet
- Enthält die gewährten Berechtigungen (Scopes)

### Refresh Token

- Langlebig (Tage bis Monate)
- Dient dem Bezug eines neuen Access Tokens ohne erneute Benutzerinteraktion
- Wird ausschließlich zwischen Client und Authorization Server ausgetauscht

### Authorization Code

- Einmalig verwendbar, kurzlebig
- Wird nach Zustimmung des Nutzers ausgestellt
- Muss vom Client gegen ein Access Token eingetauscht werden

---

## 4. Grant Types (Flows)

OAuth 2.0 definiert mehrere Flows für unterschiedliche Client-Typen. Die Wahl hängt davon ab, ob der Client ein Geheimnis sicher speichern kann und in welcher Umgebung er läuft.

---

### 4.1 Authorization Code Flow

**Anwendungsfall:** Server-seitige Webanwendungen mit Backend, die ein `client_secret` sicher speichern können.

**Ablauf:**

```
Benutzer          Client (Backend)       Auth Server         Resource Server
   │                    │                     │                     │
   │─ (1) Aktion ──────▶│                     │                     │
   │                    │── (2) Redirect ─────▶│                     │
   │                    │   /authorize?        │                     │
   │                    │   response_type=code │                     │
   │                    │   &client_id=...     │                     │
   │                    │   &scope=calendar    │                     │
   │                    │   &redirect_uri=...  │                     │
   │◀── (3) Login-Seite ─────────────────────│                     │
   │── (4) Credentials + Zustimmung ────────▶│                     │
   │                    │◀─ (5) Redirect ─────│                     │
   │                    │   ?code=abc123       │                     │
   │                    │                     │                     │
   │                    │── (6) POST /token ──▶│                     │
   │                    │   code=abc123        │                     │
   │                    │   client_secret=...  │                     │
   │                    │◀─ (7) Access Token ──│                     │
   │                    │    + Refresh Token   │                     │
   │                    │                     │                     │
   │                    │── (8) API-Call ──────────────────────────▶│
   │                    │   Authorization:     │                     │
   │                    │   Bearer <token>     │                     │
   │◀── (9) Daten ──────│◀─────────────────────────────────────────│
```

**Sicherheitseigenschaften:**

- Der Authorization Code ist ohne `client_secret` nicht einlösbar
- Der Access Token verbleibt im Backend und wird dem Browser nicht exponiert
- Der `state`-Parameter verhindert CSRF-Angriffe

---

### 4.2 Authorization Code Flow mit PKCE

**Anwendungsfall:** Single-Page-Apps, Mobile Apps, Desktop-Apps – Public Clients ohne sicher speicherbares `client_secret`.

PKCE (Proof Key for Code Exchange) ersetzt das `client_secret` durch einen dynamisch erzeugten kryptografischen Nachweis.

**Ablauf:**

```
1. Client erzeugt einen zufälligen String:  code_verifier
2. Client berechnet:                        code_challenge = SHA256(code_verifier)
3. Client sendet code_challenge             ──▶  /authorize
4. Auth Server speichert code_challenge
5. Benutzer authentifiziert sich und stimmt zu
6. Auth Server gibt Authorization Code zurück
7. Client sendet code + code_verifier       ──▶  /token
8. Auth Server prüft: SHA256(code_verifier) == code_challenge
9. Bei Übereinstimmung: Access Token wird ausgestellt
```

Ein abgefangener Authorization Code ist ohne den `code_verifier` nicht einlösbar. Der `code_verifier` wird nie über den Browser übertragen.

Seit OAuth 2.1 ist PKCE für alle Client-Typen verpflichtend – auch für serverseitige Anwendungen.

---

### 4.3 Client Credentials Flow

**Anwendungsfall:** Maschine-zu-Maschine-Kommunikation (M2M) ohne Benutzerkontext. Der Client greift auf eigene Ressourcen zu. Es gibt keinen Resource Owner.

**Ablauf:**

```
Client (Service)              Auth Server              Resource Server
     │                            │                          │
     │── (1) POST /token ────────▶│                          │
     │   grant_type=              │                          │
     │   client_credentials       │                          │
     │   client_id=...            │                          │
     │   client_secret=...        │                          │
     │◀── (2) Access Token ───────│                          │
     │                            │                          │
     │── (3) API-Call ───────────────────────────────────────▶│
     │◀── (4) Daten ─────────────────────────────────────────│
```

Einsatzgebiete: Microservice-Kommunikation, Batch-Jobs, Hintergrundprozesse.

---

### 4.4 Device Authorization Flow

**Anwendungsfall:** Geräte mit eingeschränkter Eingabemöglichkeit (Smart-TVs, Konsolen, CLI-Tools, IoT).

**Ablauf:**

```
Gerät                           Auth Server          Benutzer (am Zweitgerät)
     │                              │                        │
     │── (1) POST /device ─────────▶│                        │
     │   client_id=...              │                        │
     │◀── (2) device_code,  ────────│                        │
     │       user_code,             │                        │
     │       verification_uri       │                        │
     │                              │                        │
     │── (3) Anzeige: ───────────────────────────────────────▶│
     │   "Öffne example.com/activate"                         │
     │   "Code: WDJB-MJHT"                                   │
     │                              │◀── (4) URL aufrufen ───│
     │                              │◀── (5) Code eingeben ──│
     │                              │◀── (6) Zustimmung ─────│
     │                              │                        │
     │── (7) Polling POST /token ──▶│                        │
     │   device_code=...            │                        │
     │◀── (8) Access Token ─────────│                        │
```

---

### 4.5 Veraltete Flows

| Flow | Problem | Status |
|------|---------|--------|
| **Implicit Flow** | Token direkt in der URL exponiert, kein Refresh Token | In OAuth 2.1 entfernt. Ersatz: Authorization Code + PKCE |
| **Resource Owner Password Credentials** | Benutzer gibt Passwort an Drittanbieter-App weiter | In OAuth 2.1 entfernt |

---

## 5. Scopes

Scopes definieren den Umfang des gewährten Zugriffs. Der Benutzer bestätigt die angeforderten Scopes auf der Zustimmungsseite des Authorization Servers.

| Scope | Bedeutung |
|-------|-----------|
| `read:calendar` | Kalendereinträge lesen |
| `write:calendar` | Kalendereinträge erstellen/ändern |
| `openid profile email` | Identitätsdaten via OpenID Connect |
| `repo` | Vollzugriff auf GitHub-Repositories |

Clients sollten nur die tatsächlich benötigten Scopes anfordern (Principle of Least Privilege).

---

## 6. Refresh Token Rotation

### Problem

Refresh Tokens sind langlebig. Wird ein Refresh Token gestohlen, kann ein Angreifer damit wiederholt neue Access Tokens beziehen – potenziell über einen langen Zeitraum. Der legitime Benutzer bemerkt dies nicht, solange sein eigener Zugriff weiterhin funktioniert.

### Mechanismus

Bei Refresh Token Rotation gibt der Authorization Server bei jedem Refresh-Vorgang nicht nur einen neuen Access Token, sondern auch einen **neuen Refresh Token** aus. Der zuvor verwendete Refresh Token wird sofort invalidiert.

```
Client                          Auth Server
  │                                  │
  │── (1) POST /token ──────────────▶│
  │   grant_type=refresh_token       │
  │   refresh_token=RT_1             │
  │                                  │  RT_1 wird invalidiert
  │◀── (2) Access Token (neu) ──────│
  │       Refresh Token RT_2         │  RT_2 wird gespeichert
  │                                  │
  │        ... Token läuft ab ...    │
  │                                  │
  │── (3) POST /token ──────────────▶│
  │   grant_type=refresh_token       │
  │   refresh_token=RT_2             │
  │                                  │  RT_2 wird invalidiert
  │◀── (4) Access Token (neu) ──────│
  │       Refresh Token RT_3         │  RT_3 wird gespeichert
  │                                  │
```

Jeder Refresh Token ist also genau einmal verwendbar. Nach Einlösung existiert nur der jeweils neueste Token.

### Erkennung kompromittierter Tokens (Replay Detection)

Wird ein bereits invalidierter Refresh Token erneut verwendet, liegt ein Missbrauchsversuch vor. Der Authorization Server erkennt dies und reagiert:

```
Angreifer (mit gestohlenem RT_1)        Auth Server
  │                                          │
  │── POST /token ──────────────────────────▶│
  │   refresh_token=RT_1                     │
  │                                          │  RT_1 wurde bereits
  │                                          │  eingelöst → Replay erkannt
  │                                          │
  │                                          │  Gegenmaßnahme:
  │                                          │  Alle Tokens der
  │                                          │  Token-Familie invalidieren
  │                                          │  (RT_2, RT_3, ...)
  │◀── HTTP 400 ────────────────────────────│
  │   {"error": "invalid_grant"}             │
```

Der Authorization Server invalidiert die gesamte **Token-Familie** – alle Refresh Tokens, die aus demselben ursprünglichen Grant hervorgegangen sind. Sowohl der Angreifer als auch der legitime Client verlieren den Zugriff. Der Benutzer muss sich erneut authentifizieren.

### Token-Familien

Der Authorization Server verknüpft alle Refresh Tokens, die aus einem einzelnen Autorisierungsvorgang entstanden sind, zu einer Token-Familie:

```
Initialer Grant
     │
     ├── RT_1 (ausgegeben bei Authorization)
     │    │
     │    └── RT_2 (ausgegeben bei Refresh von RT_1)
     │         │
     │         └── RT_3 (ausgegeben bei Refresh von RT_2)
     │              │
     │              └── RT_4 (ausgegeben bei Refresh von RT_3)
     │
     └── Alle gehören zur selben Familie.
         Replay von RT_1 oder RT_2 → gesamte Familie wird invalidiert.
```

### Vergleich: Mit und ohne Rotation

| Aspekt | Ohne Rotation | Mit Rotation |
|--------|---------------|--------------|
| Gültigkeit des Refresh Tokens | Bis zum Ablaufdatum | Bis zur nächsten Verwendung |
| Auswirkung eines gestohlenen Tokens | Angreifer hat Zugriff bis Token abläuft | Angreifer kann Token maximal einmal nutzen, Replay wird erkannt |
| Erkennung von Diebstahl | Nicht möglich | Durch Replay Detection |
| Reaktion auf Diebstahl | Keine automatische | Invalidierung der gesamten Token-Familie |
| Komplexität | Gering | Authorization Server muss Token-Familien verwalten |

### Sender-Constrained Tokens als Alternative

Neben Rotation existiert ein zweiter Ansatz: **Sender-Constrained Tokens**. Dabei wird der Refresh Token kryptografisch an den Client gebunden (z. B. über mTLS oder DPoP). Ein gestohlener Token ist auf einem anderen Gerät nicht verwendbar, da der kryptografische Nachweis fehlt.

| Mechanismus | Prinzip | Vorteil | Nachteil |
|-------------|---------|---------|----------|
| **Rotation** | Token nach Einmalverwendung austauschen | Einfach implementierbar, keine Client-Zertifikate nötig | Race Conditions bei parallelen Requests möglich |
| **mTLS** | Token an Client-Zertifikat binden | Token ist auf anderem Gerät wertlos | Erfordert PKI-Infrastruktur |
| **DPoP** | Token an asymmetrisches Schlüsselpaar binden | Kein Zertifikat nötig, funktioniert auch in Browsern | Erfordert DPoP-Header bei jedem Request |

OAuth 2.1 empfiehlt entweder Rotation oder Sender-Constraining für alle Refresh Tokens.

---

## 7. Sicherheitsmaßnahmen

| Bedrohung | Gegenmaßnahme |
|-----------|----------------|
| Authorization Code Diebstahl | PKCE, kurze Gültigkeit |
| CSRF-Angriffe | `state`-Parameter |
| Token-Diebstahl | Kurze Lebensdauer, ausschließlich HTTPS |
| Token-Replay | Audience-Restriction, Token-Binding |
| Offene Redirects | Exakte Validierung der `redirect_uri` |
| Refresh-Token-Missbrauch | Token-Rotation, Sender-Constrained Tokens |

---

## 8. OAuth 2.0 vs. OAuth 2.1

OAuth 2.1 konsolidiert bestehende Best Practices und Security-RFCs in eine einzelne Spezifikation.

| Aspekt | OAuth 2.0 | OAuth 2.1 |
|--------|-----------|-----------|
| PKCE | Optional | Verpflichtend |
| Implicit Flow | Definiert | Entfernt |
| Password Grant | Definiert | Entfernt |
| Redirect-URI-Vergleich | Flexibles Matching | Exakter String-Vergleich |
| Refresh Tokens | Keine Vorgaben zur Rotation | Rotation oder Sender-Constraining empfohlen |

---

## 9. Praxisbeispiel: Spotify Authorization Code + PKCE

Das folgende Beispiel zeigt die Umsetzung des Authorization Code Flows mit PKCE in einer clientseitigen JavaScript-Anwendung (Single-Page-App), die auf die Spotify Web API zugreift.

### Rollenverteilung im Projekt

| OAuth-Rolle          | Umsetzung im Projekt                          |
|----------------------|------------------------------------------------|
| Resource Owner       | Der Spotify-Nutzer                             |
| Client               | Die SPA (Vite-App im Browser)                  |
| Authorization Server | `accounts.spotify.com`                         |
| Resource Server      | `api.spotify.com`                              |

### Verwendeter Flow

**Authorization Code Flow mit PKCE** – die Anwendung läuft vollständig im Browser und kann kein `client_secret` sicher speichern. PKCE ersetzt das Secret durch das `code_verifier` / `code_challenge`-Verfahren.

### Schritt 1: PKCE-Parameter erzeugen

Der Client generiert einen zufälligen `code_verifier` und berechnet daraus die `code_challenge` mittels SHA-256:

```javascript
function base64UrlEncode(buffer) {
  return btoa(String.fromCharCode.apply(null, new Uint8Array(buffer)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

function generateCodeVerifier() {
  const array = new Uint8Array(64);
  crypto.getRandomValues(array);
  return base64UrlEncode(array);
}

async function generateCodeChallenge(verifier) {
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  const hashed = await crypto.subtle.digest('SHA-256', data);
  return base64UrlEncode(hashed);
}
```

Der `code_verifier` wird im `sessionStorage` zwischengespeichert, da er nach dem Redirect für den Token-Austausch benötigt wird.

### Schritt 2: Redirect zum Authorization Server

Der Client leitet den Nutzer zu Spotify weiter. Die URL enthält `code_challenge` und `code_challenge_method`, aber nicht den `code_verifier`:

```javascript
const codeVerifier = generateCodeVerifier();
const codeChallenge = await generateCodeChallenge(codeVerifier);

sessionStorage.setItem('spotify_code_verifier', codeVerifier);

const params = new URLSearchParams({
  response_type: 'code',
  client_id: CLIENT_ID,
  scope: SCOPES,
  redirect_uri: REDIRECT_URI,
  code_challenge_method: 'S256',
  code_challenge: codeChallenge,
  show_dialog: 'true'
});

window.location = `https://accounts.spotify.com/authorize?${params.toString()}`;
```

### Angeforderte Scopes

Die Anwendung fordert ausschließlich lesende Berechtigungen an:

| Scope                           | Berechtigung                                  |
|---------------------------------|-----------------------------------------------|
| `user-read-private`             | Profildaten lesen                             |
| `user-read-email`               | E-Mail-Adresse lesen                          |
| `user-top-read`                 | Top-Tracks und Top-Artists lesen              |
| `playlist-read-private`         | Private Playlists lesen                       |
| `playlist-read-collaborative`   | Kollaborative Playlists lesen                 |

### Schritt 3: Authorization Code gegen Access Token tauschen

Nach dem Redirect zurück zur App extrahiert der Client den `code` aus der URL und sendet ihn zusammen mit dem `code_verifier` an den Token-Endpunkt:

```javascript
const urlParams = new URLSearchParams(window.location.search);
const code = urlParams.get('code');
const codeVerifier = sessionStorage.getItem('spotify_code_verifier');

const body = new URLSearchParams({
  grant_type: 'authorization_code',
  code,
  redirect_uri: REDIRECT_URI,
  client_id: CLIENT_ID,
  code_verifier: codeVerifier
});

const resp = await fetch('https://accounts.spotify.com/api/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: body.toString()
});

const data = await resp.json();
data.expires_at = Date.now() + data.expires_in * 1000;
sessionStorage.setItem('spotify_auth', JSON.stringify(data));
```

Der Authorization Server prüft `SHA256(code_verifier) == code_challenge`. Bei Übereinstimmung wird ein Access Token ausgestellt. Zusätzlich berechnet der Client aus `expires_in` einen absoluten Zeitstempel `expires_at`, um den Token-Ablauf proaktiv erkennen zu können.

### Schritt 4: API-Zugriff mit Bearer Token und automatischem Refresh

Der Access Token wird bei jedem Request als `Authorization: Bearer`-Header an den Resource Server gesendet. Vor jedem Request prüft der Client, ob der Token in weniger als 60 Sekunden abläuft, und erneuert ihn gegebenenfalls proaktiv. Schlägt ein Request dennoch mit HTTP 401 fehl, wird ein Refresh-Versuch unternommen und der Request wiederholt:

```javascript
async function apiGet(path) {
  let auth = getStoredAuth();
  if (!auth || !auth.access_token) throw new Error('Not authenticated');

  // Proaktiver Refresh: Token erneuern, bevor er abläuft
  if (auth.expires_at && Date.now() > auth.expires_at - 60000) {
    auth = await refreshAccessToken();
  }

  let resp = await fetch(`https://api.spotify.com/v1${path}`, {
    headers: { Authorization: `Bearer ${auth.access_token}` }
  });

  // Reaktiver Refresh: bei 401 Token erneuern und Request wiederholen
  if (resp.status === 401) {
    auth = await refreshAccessToken();
    resp = await fetch(`https://api.spotify.com/v1${path}`, {
      headers: { Authorization: `Bearer ${auth.access_token}` }
    });
  }

  return await resp.json();
}
```

### Schritt 5: Refresh Token Flow

Wenn der Access Token abgelaufen ist, sendet der Client den `refresh_token` an den Token-Endpunkt. Der Authorization Server antwortet mit einem neuen Access Token und potenziell einem neuen Refresh Token (Token Rotation, siehe Abschnitt 6):

```javascript
async function refreshAccessToken() {
  const auth = getStoredAuth();

  const body = new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: auth.refresh_token,
    client_id: CLIENT_ID
  });

  const resp = await fetch('https://accounts.spotify.com/api/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString()
  });

  const data = await resp.json();

  const newAuth = {
    ...auth,
    access_token: data.access_token,
    expires_in: data.expires_in,
    expires_at: Date.now() + data.expires_in * 1000,
    // Neuer Refresh Token überschreibt den alten (Rotation)
    ...(data.refresh_token ? { refresh_token: data.refresh_token } : {})
  };

  sessionStorage.setItem('spotify_auth', JSON.stringify(newAuth));
  return newAuth;
}
```

Enthält die Antwort ein `refresh_token`-Feld, ersetzt der Client den bisherigen Refresh Token. Das entspricht der in Abschnitt 6 beschriebenen Refresh Token Rotation: Der alte Token wird serverseitig invalidiert, der neue Token ist ab sofort der einzig gültige. Der Client muss diesen Austausch bei jedem Refresh korrekt durchführen, da ein erneutes Senden des alten Tokens als Replay erkannt und die gesamte Token-Familie invalidiert wird.

### Einordnung in die OAuth-Theorie

| Konzept aus der Theorie               | Umsetzung im Code                                                      |
|---------------------------------------|-------------------------------------------------------------------------|
| PKCE (Abschnitt 4.2)                 | `generateCodeVerifier()`, `generateCodeChallenge()`, `code_verifier` im Token-Request |
| Scopes (Abschnitt 5)                 | `SCOPES`-Variable mit fünf lesenden Berechtigungen                      |
| Refresh Token Rotation (Abschnitt 6) | `refreshAccessToken()` speichert neuen Refresh Token, falls die Antwort einen enthält |
| Token-Ablauf-Handling                 | Proaktive Prüfung via `expires_at` vor jedem Request, reaktiver Retry bei HTTP 401 |
| Token-Speicherung                     | `sessionStorage` – Token wird nicht persistiert und überlebt keinen Tab-Wechsel |
| Kein `client_secret`                  | Public Client – Secret wird weder gespeichert noch übertragen           |
| Bearer Token (Abschnitt 3)           | `Authorization: Bearer <token>` bei jedem API-Call                      |



## 10. Zusammenfassung

OAuth 2.0 ermöglicht delegierte Autorisierung: Eine Anwendung erhält eingeschränkten Zugriff auf Benutzerressourcen, ohne deren Zugangsdaten zu kennen.

Tragende Prinzipien:

1. **Rollentrennung** – Resource Owner, Client, Authorization Server und Resource Server haben getrennte Verantwortlichkeiten
2. **Token-basierter Zugriff** – Zeitlich und funktional begrenzte Tokens ersetzen die Weitergabe von Passwörtern
3. **Minimale Berechtigung** – Scopes beschränken den Zugriff auf das Erforderliche
4. **Flow-Auswahl nach Client-Typ** – Jeder Anwendungstyp verwendet den für seine Umgebung geeigneten Autorisierungsablauf

---

[oAuth](https://auth0.com/intro-to-iam/what-is-oauth-2)

[oAuth Doku](https://auth0.com/docs/quickstart/webapp/java/interactive)

[oAuth Refresh Tokens](https://auth0.com/blog/refresh-tokens-what-are-they-and-when-to-use-them/)

[Spotifiy Authorization](https://developer.spotify.com/documentation/web-api)

[oAuth in Javascript](https://auth0.com/docs/quickstart/spa/vanillajs)
