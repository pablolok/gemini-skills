namespace Tests.Samples.CSharp;

public class NonCompliantService
{
    private readonly DatabaseConnection _db;

    public NonCompliantService()
    {
        // VIOLATION: Hidden 'new' dependency (Rule 5)
        _db = new DatabaseConnection("Server=myserver;Database=mydb;");
    }

    public void DoSomething()
    {
        // VIOLATION: Console.WriteLine instead of ILogger (Rule 9)
        System.Console.WriteLine("Doing something...");
        _db.Open();
    }
}

public class DatabaseConnection(string connectionString)
{
    public void Open() { }
}
